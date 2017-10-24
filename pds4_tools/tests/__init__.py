from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import os


class PDS4ToolsTestCase(object):

    def setup(self):
        self.data_dir = os.path.join(os.path.dirname(__file__), 'data')

    def data(self, filename):
        return os.path.join(self.data_dir, filename)