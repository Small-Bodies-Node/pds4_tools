from __future__ import absolute_import
from __future__ import print_function
from __future__ import division
from __future__ import unicode_literals


class PDS4StandardsException(Exception):
    """ Custom exception thrown when PDS4 Standards are violated. """
    pass


class PDS4ToolsDeprecationWarning(UserWarning):
    """ Custom depreciation warning issued when a deprecated PDS4 tools feature is used.

    Notes
    -----
    Inherits from UserWarning rather than DeprecationWarning because the latter is not
    necessarily shown to user by default.

    Parameters
    ----------
    message : str, optional
        Message to show to user. When given, all other options are ignored.
    name : str, optional
        Name of feature that is deprecated. Required when *message* is absent.
    obj_type : str, optional
        Type of feature that is deprecated; e.g., function or class.  Required when *message* is absent.
    since : str, optional
        Version from which feature is deprecated.  Required when *message* is absent.
    removal : str, optional
        Version from which feature may be removed.
    addendum : str, optional
        An addendum following the main deprecation message.
    """

    def __init__(self, message=None, name=None, obj_type=None, since=None, removal=None, addendum=None):

        if not message:
            message = ('\nThe {} {} was deprecated in PDS4 Tools {}'.format(name, obj_type, since)
                    + (' and may be removed in {}.'.format(removal) if removal else '.')
                    + (' {}'.format(addendum) if addendum else ''))

        super(PDS4ToolsDeprecationWarning, self).__init__(message)
