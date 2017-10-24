from __future__ import absolute_import
from __future__ import print_function
from __future__ import division
from __future__ import unicode_literals


class PDS4StandardsException(Exception):
    """ Custom exception thrown when PDS4 Standards are violated. """
    pass


class PDS4ToolsDeprecationWarning(DeprecationWarning):
    """ Custom depreciation warning issued when a depreciated PDS4 tools feature is used. """
    pass
