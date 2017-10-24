from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

from .label_view import SearchableTextWindow


class HeaderViewWindow(SearchableTextWindow):
    """ Window used to display character version of PDS4 Header objects. """

    def __init__(self, viewer, text):

        # Set initial necessary variables and do other required initialization procedures
        super(HeaderViewWindow, self).__init__(viewer, header='Header', text=text)


def open_header(viewer, header_structure):
    """ Open an image view for an ArrayStructure.

    Parameters
    ----------
    viewer : PDS4Viewer
        An instance of PDS4Viewer.
    header_structure : HeaderStructure
        A parsable header structure to visualize as text.

    Returns
    -------
    HeaderViewWindow
        The window instance for header view.
    """

    text = header_structure.parser().to_string()
    header_window = HeaderViewWindow(viewer, text=text)

    return header_window
