from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import sys
import xml.etree.ElementTree as ET

import numpy as np


PY26 = sys.version_info[0:2] == (2, 6)

# ElementTree compat (Python 2.7+ and 3.3+)
ET_Element = ET._Element if PY26 else ET.Element

# NumPy compat (NumPy 2.0+)
try:
    np_unicode = np.unicode_
except AttributeError:
    np_unicode = np.str_
