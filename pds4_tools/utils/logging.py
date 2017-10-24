from __future__ import absolute_import
from __future__ import print_function
from __future__ import division
from __future__ import unicode_literals

import sys
import logging

# Minimum logging levels for loud and quiet operation
_loud = logging.DEBUG
_quiet = logging.ERROR


def logger_init():
    """ Initializes or obtains the logger and its handlers.

    Returns
    -------
    PDS4Logger
        The global logger for all pds4 tools.
    """

    logging.setLoggerClass(PDS4Logger)
    logger = logging.getLogger('PDS4ToolsLogger')
    logger.setLevel(_loud)

    # If this is a new logger then initialize its config
    if not logger.handlers:

        # Create the stdout handler. This handler outputs to stdout and to warning and errors message boxes
        # in the viewer and can be silenced by user (via use of quiet or --quiet).
        stdout_handler = PDS4StreamHandler('stdout_handler')

        # Create the log handler. This handler does not output to stdout or to screen and should not
        # be silenced.
        log_handler = PDS4SilentHandler('log_handler')

        # Create the formatter and add it to the handlers
        formatter = PDS4Formatter()
        stdout_handler.setFormatter(formatter)
        log_handler.setFormatter(formatter)

        # Add handlers to logger.
        logger.addHandler(stdout_handler)
        logger.addHandler(log_handler)

    return logger


class PDS4Logger(logging.Logger, object):
    """ Customer Logger that supports getting handlers by name, has quiet() and loud() methods
        and where each logging message can have a maximum number of repetitions set. """

    def __init__(self, *args, **kwargs):

        # Stores those messages (as keys) which have a max_repeat argument set (see _log() details)
        # and the number of repetitions they have had (as values)
        self._max_repeat_records = {}

        super(PDS4Logger, self).__init__(*args, **kwargs)

    def get_handler(self, handler_name):
        """ Obtain handler by name.

        Parameters
        ----------
        handler_name : str or unicode
            The name of the handler.

        Returns
        -------
        PDS4StreamHandler or PDS4SilentHandler
            Handler for this logger, matching the *handler_name*.
        """

        for handler in self.handlers:

            if handler.name == handler_name:
                return handler

        return None

    def quiet(self, handler_name='stdout_handler'):
        """ Sets a handler to log only errors.

        Parameters
        ----------
        handler_name : str or unicode, optional
            Handler name to select. Defaults to stdout handler.

        Returns
        -------
        None
        """
        self.get_handler(handler_name).setLevel(_quiet)

    def loud(self, handler_name='stdout_handler'):
        """ Sets a handler to log warnings and above.

        Parameters
        ----------
        handler_name : str or unicode, optional
            Handler name to select.  Defaults to stdout handler.

        Returns
        -------
        None
        """

        self.get_handler(handler_name).setLevel(_loud)

    def is_quiet(self, handler_name='stdout_handler'):
        """ Obtains whether a handler is quiet.

        Parameters
        ----------
        handler_name : str or unicode, optional
            Handler name to select.  Defaults to stdout handler.

        Returns
        -------
        bool
            True if the logger is quiet, i.e. logs only errors; false otherwise.
        """
        return self.get_handler(handler_name).is_quiet

    def _log(self, *args, **kwargs):
        """
        Subclassed to allow a *max_repeat* argument to every logger log call (e.g. ``logger.info``,
        ``logger.warning``, etc). When given, the indicated message will only be emitted the number
        of times indicated.

        Returns
        -------
        None
        """

        msg = args[1]
        max_repeat = kwargs.pop('max_repeat', None)

        if max_repeat is not None:

            times_repeated = self._max_repeat_records.setdefault(msg, 0)
            self._max_repeat_records[msg] += 1

            if times_repeated >= max_repeat:
                return

        super(PDS4Logger, self)._log(*args, **kwargs)


class PDS4StreamHandler(logging.StreamHandler):
    """ Custom StreamHandler that has a *name* and a *is_quiet* attributes. """

    def __init__(self, name, level=_loud):
        """ Initialize the handler.

        Parameters
        ----------
        name : str or unicode
            Name to give the handler.
        level : int, optional
            Default log level for this handler. Defaults to _loud.
        """

        # Using try due to stream parameter being renamed in Python <2.7)
        try:
            logging.StreamHandler.__init__(self, stream=sys.stdout)
        except TypeError:
            logging.StreamHandler.__init__(self, strm=sys.stdout)

        self._name = name
        self._is_quiet = None

        self.set_level(level)

    @property
    def name(self):
        """
        Returns
        -------
        str or unicode
            Name of the handler.
        """
        return self._name

    @property
    def is_quiet(self):
        """
        Returns
        -------
        bool
            True if handler is quiet, False otherwise.
        """
        return self._is_quiet

    def set_level(self, level):
        """ Set handler log level.

        Convenience method for setLevel.

        Parameters
        ----------
        level : int
            Level to set for handler. See Python documentation on logger levels for details.
        """
        self.setLevel(level)

    def get_level(self):
        """ Get handler log level.

        Convenience method for the *level* attribute.

        Returns
        -------
        int
            Level for handler. See Python do cumentation on logger levels for details.
        """
        return self.level

    def setLevel(self, level):
        """ Set handler log level.

        Overloads ``logging.StreamHandler.setLevel`` to automatically set whether logger is quiet or loud.

        Parameters
        ----------
        level : int
            Level to set for handler. See Python documentation on logger levels for details.
        """

        if level == _quiet:
            self._is_quiet = True
        else:
            self._is_quiet = False

        logging.StreamHandler.setLevel(self, level)


class PDS4SilentHandler(PDS4StreamHandler):
    """ Custom StreamHandler that saves emitted records to *records* attribute.

    Able to print out previously emitted records via `to_string`. """

    def __init__(self, name):

        PDS4StreamHandler.__init__(self, name)

        self.records = []
        self._recording_start = None

    def emit(self, record):
        """ Saves emitted record.

        Parameters
        ----------
        record : logger.LogRecord
            Record to emit.

        Returns
        -------
        None
        """
        self.records.append(record)

    def begin_recording(self):
        """
        Used in conjunction with `get_recording`. Records emitted after this method is called will be
        returned by `get_recording`.

        Returns
        -------
        None
        """
        self._recording_start = len(self.records)

    def get_recording(self, reset=True):
        """
        Obtains records since `begin_recording` was called as a joined string.

        Parameters
        ----------
        reset : bool, optional
            If True, begins a new recording from now on. If False, recording from previous point
            continues. Defaults to True.

        Returns
        -------
        str or unicode
            A string containing the messages that were emitted since `begin_recording` was called.

        Raises
        ------
        RuntimeError
            Raised if `begin_recording` was not called prior to calling this method.
        """
        record_start = self._recording_start

        if record_start is None:
            raise RuntimeError('Cannot obtain recording: no recording was started.')

        if reset:
            self.begin_recording()

        return self.to_string(start_i=record_start)

    def to_string(self, start_i=0, end_i=None):
        """ Output emitted records as a joined string.

        Parameters
        ----------
        start_i : int, optional
            Index of first record to include. Defaults to 0 (include records from the beginning).
        end_i : int, optional
            Index of last record to include. Defaults to None (include records until the end).

        Returns
        -------
        str or unicode
            A string containing the messages in the records that were previously emitted.
        """

        formatted_records = [self.format(record) for record in self.records[start_i:end_i]]

        return '\n'.join(formatted_records)


class PDS4Formatter(logging.Formatter):
    """ Custom formatter that varies format according to log level. """

    def format(self, record):
        """
        Parameters
        ----------
        record : logger.LogRecord
            The record to format.

        Returns
        -------
        str or unicode
            The formatted record string.

        """
        formatter = logging.Formatter('%(message)s')
        formatted_value = logging.Formatter.format(formatter, record)

        if record.levelno != logging.INFO:
            formatted_value = record.levelname.capitalize() + ': ' + formatted_value

        return formatted_value
