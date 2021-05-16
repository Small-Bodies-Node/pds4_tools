from __future__ import absolute_import
from __future__ import print_function
from __future__ import division
from __future__ import unicode_literals

import inspect
from xml.etree import ElementTree as ET

from ..extern import six

# OrderedDict compat (Python 2.7+ and 3.1+)
try:
    from collections import OrderedDict
except ImportError:
    from ..extern.ordered_dict import OrderedDict

# ArgParse compat (Python 2.7+ and 3.2+)
try:
    import argparse
except ImportError:
    from ..extern import argparse

# ElementTree compat (Python 2.7+ and 3.3+)
ET_Element = ET.Element if isinstance(ET.Element, six.class_types) else ET._Element
ET_Tree_iter = ET.ElementTree.iter if hasattr(ET.ElementTree, 'iter') else ET.ElementTree.getiterator
ET_Element_iter = ET_Element.iter if hasattr(ET_Element, 'iter') else ET_Element.getiterator
ET_ParseError = ET.ParseError if hasattr(ET, 'ParseError') else None


# signature.bind(...).arguments compat (Python 3.3+)
def bind_arguments(func, *args, **kwargs):
    # Python 3.3+
    try:
        signature = inspect.signature(func)
        arguments = signature.bind(*args, **kwargs).arguments
    except AttributeError:
        # Python 2.7+
        try:
            arguments = inspect.getcallargs(func, *args, **kwargs)
            defaults = inspect.getcallargs(func, (), ())
            for arg in arguments.keys():
                if (defaults[arg] == arguments[arg]) and (arg not in kwargs):
                    del arguments[arg]
        except AttributeError:
            arguments = kwargs

    return arguments
