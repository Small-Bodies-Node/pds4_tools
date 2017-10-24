from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import os
import math
import platform
import functools
import traceback

from . import label_view, table_view, header_view, cache
from .core import Window, MessageWindow
from .widgets.scrolled_frame import ScrolledFrame
from .widgets.tooltip import ToolTip
from .table_view import array_structure_to_table

from ..reader.core import pds4_read
from ..reader.read_tables import table_data_size_check

from ..utils.logging import logger_init

from ..extern import six
from ..extern.six.moves.tkinter import (Menu, Canvas, Frame, Scrollbar, Label, Button, BooleanVar)
from ..extern.six.moves.tkinter_tkfiledialog import askopenfilename

# Initialize the logger
logger = logger_init()

#################################


class StructureListWindow(Window):
    """ Window that summarizes the structures showing some of their properties and giving buttons to open them """

    def __init__(self, viewer, quiet=False, lazy_load=False, show_headers=False):

        # Set initial necessary variables and do other required initialization procedures
        super(StructureListWindow, self).__init__(viewer, withdrawn=False)

        # Set window width to not be resizable
        self._widget.resizable(width=0, height=1)

        # Initialize structure list window variables
        self._canvas = None
        self._scrolled_frame = None
        self._structure_list = None
        self._recent_menu = None
        self._label_open = False

        # Create menu
        self._menu = Menu(self._widget)
        self._widget.config(menu=self._menu)
        self._add_menu(quiet, lazy_load, show_headers)

        # Add notify event for scroll wheel (used to scroll structure list)
        self._bind_scroll_event(self._mousewheel_scroll)

    # Opens the label, reads in any structures it contains, calls _draw_summary()
    def open_label(self, filename=None, from_existing_structures=None):

        if (filename is None) and (from_existing_structures is None):
            raise TypeError('Cannot open a label without either a filename or existing StructureList.')

        # Reset the summary if a label is already open
        if self._label_open:
            self.reset()

        # Open the label and data, or show an error if one occurs
        try:

            # Lazy-load all structures from file (to obtain meta data)
            if filename is not None:

                self._structure_list = pds4_read(filename, quiet=self.menu_option('quiet'),
                                                 lazy_load=True, decode_strings=False)

                cache.write_recently_opened(filename)

            # Load (lazy if previously was lazy) structures from existing list
            else:
                self._structure_list = from_existing_structures

            # Set title
            title = 'Data Structure Summary' if len(self._structure_list) > 0 else 'Label'
            title += '' if (filename is None) else " for '{0}'".format(filename)
            self._set_title("{0} - {1}".format(self._get_title(), title))

        except Exception as e:

            trace = traceback.format_exc()
            if isinstance(trace, six.binary_type):
                trace = trace.decode('utf-8')

            log = logger.get_handler('log_handler').get_recording()
            error = log + '\n' + trace
            MessageWindow(self._viewer, 'An Error Occurred!', error)
            logger.exception('An error occurred during label processing.')

        else:

            # Read data from file (or try to access if it exists) for each structure if lazy-load disabled
            if not self.menu_option('lazy_load'):
                self.reify_structures()

            # Draw the summary window
            self._draw_summary()
            self._label_open = True

    # Read-in the data for all unread structures
    def reify_structures(self):

        # Get list of unread structures
        unread_structures = [structure for structure in self._structure_list if not structure.data_loaded]

        # Inform user about large structures
        large_structures = []
        for structure in unread_structures:

            if structure.is_table() and table_data_size_check(structure, quiet=True):
                large_structures.append(structure)

        if large_structures:
            large_struct_message = 'The following structures: \n\n'

            for structure in large_structures:
                large_struct_message += '{0} structure: {1} \n'.format(structure.type, structure.id)

            large_struct_message += (
                '\ncontain a large amount of data. Loading them may take a while. Recommend lazy-load '
                'be enabled via the Options menu.'
            )

            warning_window = self._issue_warning(large_struct_message, log=False, show=True)

        # Read data for all unread structures
        for structure in unread_structures:

            self._reify_structure(structure, size_check=False)

    # Read-in data for a particular structure. Returns False if an error was encountered during reification.
    def _reify_structure(self, structure, size_check=True):

        # Skip reifying structure if it has already been reified
        if structure.data_loaded:
            return True

        # Initialize logging for data read-in
        exception_occurred = False
        logger.get_handler('log_handler').begin_recording()

        # On request and for large, still unread, structures issue a warning message prior to
        # attempting to read-in the data
        warning_window = None
        is_large_table = structure.is_table() and table_data_size_check(structure, quiet=True)

        if size_check and is_large_table:

            message = ("{0} structure '{1}' contains a large amount of data. This process may take "
                       "a while. Loading...".format(structure.type, structure.id))

            warning_window = self._issue_warning(message, log=False, show=True)

        # Read the data for the structure
        try:
            logger.info('Now processing a {0} structure: {1}'.format(structure.type, structure.id))
            structure.data

        except Exception:

            if structure.data_loaded:
                del structure.data

            exception_occurred = True
            logger.exception('An error occurred during data read-in.')

        # Close warning window once loading is finished
        if warning_window:
            warning_window.close()

        # Add logging messages for data read-in to log
        log = logger.get_handler('log_handler').get_recording()
        self._structure_list.read_in_log += '\n' + log

        # Show errors that occurred on loading
        if exception_occurred:
            MessageWindow(self._viewer, 'An Error Occurred!', log)

        return not exception_occurred

    # Draws a summary of the opened label onto the screen
    def _draw_summary(self):

        # Add View menu if it does not already exist
        if not self._label_open:

            view_menu = Menu(self._menu, tearoff=0)
            self._menu.add_cascade(label='View', menu=view_menu)

            view_menu.add_command(label='Full Label', command=self._open_label)

            view_menu.add_command(label='Read-In Log', command=lambda:
                MessageWindow(self._viewer, 'Label/Data Read-in Log', self._structure_list.read_in_log))

            view_menu.add_separator()

            view_menu.add_checkbutton(label='Show Headers', onvalue=True, offvalue=False,
                                      variable=self._menu_options['show_headers'])

        has_structures = len(self._structure_list) > 0
        all_headers = all(structure.is_header() for structure in self._structure_list)

        # Draw summary for structures found
        if has_structures and (not all_headers or self.menu_option('show_headers')):
            self._draw_structure_summary()

        # Draw summary that shows only the full label if no data structures to display are found
        else:
            self._draw_empty_summary()

    # Draws a summary of the label  of when the StructureList contains supported data structures
    def _draw_structure_summary(self):

        # Shorten the Name column if we only have structures with short names
        structure_names = [structure.id for structure in self._structure_list]
        name_column_size = 200 if len(max(structure_names, key=len)) > 8 else 125

        # Create main canvas (which will contain the header frame, and a structures canvas for the rest)
        self._canvas = Canvas(self._widget, highlightthickness=0)

        # Add the header
        header_frame = Frame(self._canvas, takefocus=False)
        header_frame.pack(side='top', fill='y', expand=0, anchor='nw', pady=(2, 0))

        index = Label(header_frame, text='Index', font=self.get_font(10, 'bold'))
        header_frame.grid_columnconfigure(0, minsize=100)
        index.grid(row=0, column=0)

        name = Label(header_frame, text='Name', font=self.get_font(10, 'bold'))
        header_frame.grid_columnconfigure(1, minsize=name_column_size)
        name.grid(row=0, column=1)

        type = Label(header_frame, text='Type', font=self.get_font(10, 'bold'))
        header_frame.grid_columnconfigure(2, minsize=165)
        type.grid(row=0, column=2)

        dimension = Label(header_frame, text='Dimension', font=self.get_font(10, 'bold'))
        header_frame.grid_columnconfigure(3, minsize=165)
        dimension.grid(row=0, column=3)

        # Create structures frame, which will contain all structure meta data inside it
        self._scrolled_frame = ScrolledFrame(self._canvas, vscrollmode='dynamic', hscrollmode='none')
        self._scrolled_frame.pack(side='bottom', fill='both', expand=1, pady=(12, 0))

        structures_frame = self._scrolled_frame.interior

        # Show structure meta data for each structure
        for i, structure in enumerate(self._structure_list):

            # Skips headers if requested
            if structure.is_header() and not self.menu_option('show_headers'):
                continue

            # Index
            index = Label(structures_frame, text=i, font=self.get_font())
            structures_frame.grid_columnconfigure(0, minsize=100)
            index.grid(row=i, column=0, pady=(2, 7))

            # Name or LID
            name_text = structure.id if (len(structure.id) <= 30) else structure.id[:29] + '...'
            name = Label(structures_frame, text=name_text, font=self.get_font())
            structures_frame.grid_columnconfigure(1, minsize=name_column_size)
            name.grid(row=i, column=1, pady=(2, 7))

            if len(structure.id) > 30:
                ToolTip(name, structure.id)

            # Type
            type = Label(structures_frame, text=structure.type, font=self.get_font())
            structures_frame.grid_columnconfigure(2, minsize=165)
            type.grid(row=i, column=2, pady=(2, 7))

            # Dimensions
            if structure.is_header():
                dimensions_text = '---'

            else:

                dimensions = structure.meta_data.dimensions()

                if structure.is_table():
                    dimensions_text = '{0} cols X {1} rows'.format(dimensions[0], dimensions[1])

                elif structure.is_array():
                    dimensions_text = ' X '.join(six.text_type(dim) for dim in dimensions)

            dimension = Label(structures_frame, text=dimensions_text, font=self.get_font())
            structures_frame.grid_columnconfigure(3, minsize=165)
            dimension.grid(row=i, column=3, pady=(2, 7))

            # Open Data View Buttons
            button_frame = Frame(structures_frame)
            button_frame.grid(row=i, column=4, padx=(30, 40), sticky='w')
            font = self.get_font(weight='bold')

            open_label = functools.partial(self._open_label, i)
            view_label = Button(button_frame, text='Label', font=font, width=7, command=open_label)
            view_label.pack(side='left')

            if _is_tabular(structure):
                open_table = functools.partial(self._open_table, i)
                view_table = Button(button_frame, text='Table', font=font, width=7, command=open_table)
                view_table.pack(side='left')

            if _is_plottable(structure):
                open_plot = functools.partial(self._open_plot, i)
                view_plot = Button(button_frame, text='Plot', font=font, width=7, command=open_plot)
                view_plot.pack(side='left')

            if _is_displayable(structure):
                open_image = functools.partial(self._open_image, i)
                view_image = Button(button_frame, text='Image', font=font, width=7, command=open_image)
                view_image.pack(side='left')

            if _is_parsable_header(structure):
                open_header = functools.partial(self._open_header, i)
                view_header = Button(button_frame, text='Text', font=font, width=7, command=open_header)
                view_header.pack(side='left')

        # Set the width and the initial height of the window
        self._widget.update_idletasks()

        half_screen_height = self._get_screen_size()[1] // 2
        window_height = structures_frame.winfo_height() + header_frame.winfo_reqheight() + 16
        window_width = structures_frame.winfo_reqwidth()

        if window_height > half_screen_height:

            # Find a window height such that it exactly fits the closest number of structures which can
            # fit in half the screen height (i.e. such that no structure fits only part way on the screen)
            possible_heights = [30*i + header_frame.winfo_reqheight() + 16
                                for i in range(0, len(self._structure_list))]
            window_height = min(possible_heights, key=lambda x:abs(x-half_screen_height))

        self._set_window_dimensions(window_width, window_height)

        # Add line dividing header and summary data
        self._canvas.create_line(5, 27, window_width - 5, 27)

        # Add the View text header
        view = Label(header_frame, text='View', font=self.get_font(10, 'bold'))
        view_left_pad = math.floor((window_width - 100 - name_column_size - 165 - 165) / 2 - 25)
        view_left_pad = view_left_pad if view_left_pad > 0 else 0
        view.grid(row=0, column=4, padx=(view_left_pad, 0))

        # Once all widgets are added, we pack the canvas. Packing it prior to this can result
        # in ugly resizing and redrawing as widgets are being added above.
        self._canvas.pack(fill='both', expand=1)

    # Draws a summary the label when the StructureList does not contain any supported data structures
    def _draw_empty_summary(self):

        # Create main canvas (which will contain the header frame, and a frame for the label info)
        self._canvas = Canvas(self._widget, highlightthickness=0)

        # Add the header
        header_frame = Frame(self._canvas, takefocus=False)
        header_frame.pack(side='top', fill='y', expand=0, anchor='nw', pady=(2, 0))

        type = Label(header_frame, text='Type', font=self.get_font(10, 'bold'))
        header_frame.grid_columnconfigure(0, minsize=165)
        type.grid(row=0, column=0)

        view = Label(header_frame, text='View', font=self.get_font(10, 'bold'))
        header_frame.grid_columnconfigure(1, minsize=100)
        view.grid(row=0, column=1, padx=(70, 0))

        # Create scrolled frame, which will contain info about the label
        self._scrolled_frame = ScrolledFrame(self._canvas, vscrollmode='dynamic', hscrollmode='none')
        self._scrolled_frame.pack(side='bottom', fill='both', expand=1, pady=(12, 0))

        label_info_frame = self._scrolled_frame.interior

        type = Label(label_info_frame, text=self._structure_list.type, font=self.get_font())
        label_info_frame.grid_columnconfigure(0, minsize=165)
        type.grid(row=0, column=0, pady=(2, 7))

        view_label = Button(label_info_frame, text='Full Label', font=self.get_font(weight='bold'), width=15,
                            command=self._open_label)
        header_frame.grid_columnconfigure(1, minsize=100)
        view_label.grid(row=0, column=1, padx=(30, 10), pady=(2, 7))

        # Set the width and the initial height of the window
        self._widget.update_idletasks()

        window_height = label_info_frame.winfo_height() + header_frame.winfo_reqheight() + 16
        window_width = label_info_frame.winfo_reqwidth()

        self._set_window_dimensions(window_width, window_height)

        # Add line dividing header and summary data
        self._canvas.create_line(5, 27, window_width - 5, 27)

        # Once all widgets are added, we pack the canvas. Packing it prior to this can result
        # in ugly resizing and redrawing as widgets are being added above.
        self._canvas.pack(fill='both', expand=1)

    # Opens the label view for a structure
    def _open_label(self, structure_idx=None):

        if structure_idx is None:
            initial_display = 'full label'
            structure_label = None
        else:
            initial_display = 'object label'
            structure_label = self._structure_list[structure_idx].label

        label_view.open_label(self._viewer, self._structure_list.label, structure_label, initial_display)

    # Opens a header view for a structure
    def _open_header(self, structure_idx):

        # Read-in data for the structure if that has not happened already
        structure = self._structure_list[structure_idx]
        reified = self._reify_structure(structure, size_check=True)

        # Do not attempt to open table view if an error was encountered during reification
        if not reified:
            return

        # Open a header view
        if _is_parsable_header(structure):
            header_view.open_header(self._viewer, structure)

        else:
            raise TypeError('Cannot show header view of a non-parsable structure with type ' + structure.type)

    # Opens a table view for a structure
    def _open_table(self, structure_idx):

        # Read-in data for the structure if that has not happened already
        structure = self._structure_list[structure_idx]
        reified = self._reify_structure(structure, size_check=True)

        # Do not attempt to open table view if an error was encountered during reification
        if not reified:
            return

        # Open the table view
        if _is_tabular(structure):

            if structure.is_array():
                structure = array_structure_to_table(structure, _copy_data=False)

            table_view.open_table(self._viewer, structure)

        else:
            raise TypeError('Cannot show table view of structure having type ' + structure.type)

    # Opens a plot view for a structure
    def _open_plot(self, structure_idx):

        # Import plot view; this module requires MPL, so we import it here as opposed to at the top.
        from . import plot_view

        # Read-in data for the structure if that has not happened already
        structure = self._structure_list[structure_idx]
        reified = self._reify_structure(structure, size_check=True)

        # Do not attempt to open plot view if an error was encountered during reification
        if not reified:
            return

        # Open the plot view
        if _is_plottable(structure):

            if structure.is_array():
                structure = array_structure_to_table(structure)

            plot_view.open_plot_column_select(self._viewer, structure)

        else:
            raise TypeError('Cannot show plot of non-plottable structure with type ' + structure.type)

    # Opens an image view for a structure
    def _open_image(self, structure_idx):

        # Import image view; this module requires MPL, so we import it here as opposed to at the top.
        from . import image_view

        # Read-in data for the structure if that has not happened already
        structure = self._structure_list[structure_idx]
        reified = self._reify_structure(structure, size_check=True)

        # Do not attempt to open image view if an error was encountered during reification
        if not reified:
            return

        # Open the image view
        if _is_displayable(structure):
            image_view.open_image(self._viewer, structure)

        else:
            raise TypeError('Cannot show image view of structure having type ' + structure.type)

    # Dialog window to create a new summary view for another label
    def _open_file_box(self, new_window=True):

        # On Linux, the default filetype selected goes first. On Windows it depends on the version of the
        # askopenfilename dialog being used. There is an old bug in Tkinter, at least under Windows 7, where
        # the older Windows dialog is used; and this older dialog also takes the default filetype first, but
        # the newer dialog takes it last. Ultimately this setting for Windows should be based on the system
        # that the frozen distribution is packaged, such that the correct default filetype is first. On Mac
        # adding any type seems to only allow that type to be selected, so we ignore this option.
        if platform.system() == 'Darwin':
            filetypes = []
        else:
            filetypes = [('XML Files', '.xml'), ('All Files', '*')]

        initial_dir = cache.get_last_open_dir(if_exists=True)

        filename = askopenfilename(title='Open Label',
                                   parent=self._widget,
                                   filetypes=filetypes,
                                   initialdir=initial_dir)

        # Check that filename is a string type (some OS' return binary str and some unicode for filename).
        # Also check that it is neither None or empty (also depends on OS)
        if isinstance(filename, (six.binary_type, six.text_type)) and (filename.strip() != ''):

            if new_window:
                open_summary(self._viewer, filename=filename,
                             quiet=self.menu_option('quiet'), lazy_load=self.menu_option('lazy_load'))

            else:
                self.open_label(filename)

    def _add_menu(self, quiet, lazy_load, show_headers):

        # Initialize menu options
        self._menu_options['quiet'] = BooleanVar()
        self._add_trace(self._menu_options['quiet'], 'w', self._update_quiet, default=quiet)

        self._menu_options['lazy_load'] = BooleanVar()
        self._add_trace(self._menu_options['lazy_load'], 'w', self._update_lazy_load, default=lazy_load)

        self._menu_options['show_headers'] = BooleanVar()
        self._add_trace(self._menu_options['show_headers'], 'w', self._update_show_headers, default=show_headers)

        # Create file menu
        file_menu = Menu(self._widget, tearoff=0)
        file_menu.add_command(label='Open...', command=lambda: self._open_file_box(False))
        file_menu.add_command(label='Open in New Window...', command=lambda: self._open_file_box(True))

        file_menu.add_separator()
        self._recent_menu = Menu(file_menu, tearoff=0, postcommand=self._update_recently_opened)
        file_menu.add_cascade(label='Open Recent', menu=self._recent_menu)

        file_menu.add_separator()
        file_menu.add_command(label='Exit', command=self._viewer.quit)
        self._menu.add_cascade(label='File', menu=file_menu)

        # Create options menu
        options_menu = Menu(self._widget, tearoff=0)
        options_menu.add_checkbutton(label='Lazy-Load Data', onvalue=True, offvalue=False,
                                     variable=self._menu_options['lazy_load'])
        options_menu.add_checkbutton(label='Hide Warnings', onvalue=True, offvalue=False,
                                     variable=self._menu_options['quiet'])
        self._menu.add_cascade(label='Options', menu=options_menu)

    # Updates the logger state to match current menu options value
    def _update_quiet(self, *args):

        if self.menu_option('quiet'):
            logger.quiet()

        else:
            logger.loud()

    # On disable of lazy-load, loads all data immediately
    def _update_lazy_load(self, *args):

        if self._label_open and (not self.menu_option('lazy_load')):
            self.reify_structures()

    # Updates whether Headers structures are shown in the structure summary
    def _update_show_headers(self, *args):

        if self._label_open:

            self._erase_summary()
            self._draw_summary()

    # Updates recently opened menu just prior to showing it
    def _update_recently_opened(self):

        recent_paths = cache.get_recently_opened()

        # Clear out all existing menu entries
        self._recent_menu.delete(0, self._recent_menu.index('last'))

        # Show a disabled None option if no existing paths
        if len(recent_paths) == 0:
            self._recent_menu.add_command(label='None', state='disabled')

        # Show recently opened files
        else:

            for path in recent_paths:
                self._recent_menu.add_command(label=path, command=lambda path=path: self.open_label(path))

    # Called on mouse wheel scroll action, scrolls structure list up or down if scrollbar is shown
    def _mousewheel_scroll(self, event):

        if (not self._label_open) or (not self._scrolled_frame.can_vert_scroll()):
            return

        event_delta = int(-1 * event.delta)

        if platform.system() != 'Darwin':
            event_delta //= 120

        self._scrolled_frame.yview_scroll(event_delta, 'units')

    # Erases the structure list summary as shown on the screen
    def _erase_summary(self):

        if self._label_open:

            self._scrolled_frame.destroy()
            self._canvas.destroy()

    # Resets the window to a state before any data was opened
    def reset(self):

        if self._label_open:

            self._set_title(self._get_title().split('-')[0].strip())
            self._menu.delete('View')
            self._erase_summary()
            self._structure_list = None
            self._label_open = False

    def close(self):

        self._structure_list = None
        super(StructureListWindow, self).close()


def _is_tabular(structure):
    """ Determines if a PDS4 structure can be shown as a table.

    Tabular structures are either:
        (1) Tables, or
        (2) Arrays

    Parameters
    ----------
    structure : Structure
        PDS4 structure to check.

    Returns
    -------
    bool
        True if *structure* can be displayed as a table, False otherwise.
    """

    return structure.is_table() or structure.is_array()


def _is_plottable(structure):
    """ Determines if a PDS4 structure is plottable.

    Plottable structures are either:
        (1) 1D arrays, or
        (2) Tables

    Parameters
    ----------
    structure : Structure
        PDS4 structure to check.

    Returns
    -------
    bool
        True if *structure* can be plotted, False otherwise.
    """

    plottable = False

    if structure.is_table():
        plottable = True

    elif structure.is_array() and structure.meta_data.num_axes() == 1:
        plottable = True

    return plottable


def _is_displayable(structure):
    """ Determines if a PDS4 structure is displayable as an image.

    Displayable structures are PDS4 arrays are those that are either:
        (1) a 2D array, or
        (2) sub-types of Array_2D or Array_3D, or
        (3) have a display dictionary

    Parameters
    ----------
    structure : Structure
        PDS4 structure to check.

    Returns
    -------
    bool
        True if *structure* can be displayed as an image, False otherwise.
    """

    if structure.is_array():

        has_display_dict = structure.meta_data.display_settings is not None
        is_2d_array = structure.meta_data.num_axes() == 2

        if ('Array_2D_' in structure.type) or ('Array_3D_' in structure.type) or is_2d_array or has_display_dict:
            return True

    return False


def _is_parsable_header(structure):
    """ Determines if a PDS4 header structure can be parsed into plain text.

    Header structures that can be displayed as text are:
        (1) Plain-text Headers
        (2) Headers that can be turned into plain-text via a parser

    """

    return structure.is_header() and hasattr(structure.parser(), 'to_string')


def open_summary(viewer, filename=None, from_existing_structures=None, quiet=False, lazy_load=True):
    """ Open a new structure summary window (for structures found in label).

    Shows a summary of the structures found in the label, letting the appropriate structures be
    opened as a table, plot or image. Also allows label segments and the full label to be examined.

    Parameters
    ----------
    viewer : PDS4Viewer
        An instance of PDS4Viewer.
    filename : str or unicode, optional
        The filename, including full or relative path if necessary, of
        the PDS4 label describing the data to be viewed.
    from_existing_structures : StructureList, optional
        An existing StructureList, as returned by pds4_read(), to view. Takes
        precedence if given together with filename.
    lazy_load : bool, optional
        Do not read-in data of each data structure until attempt to view said
        data structure. Defaults to True.
    quiet : bool, optional
        Suppresses all info/warnings from being output and displayed.
        Defaults to False.

    Returns
    -------
    StructureListWindow
        The window instance for the structure summary.

    """

    summary_window = StructureListWindow(viewer, quiet=quiet, lazy_load=lazy_load)

    if (filename is not None) or (from_existing_structures is not None):
        summary_window.open_label(filename=filename, from_existing_structures=from_existing_structures)

    return summary_window
