from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import os
from posixpath import join as urljoin


class PDS4ToolsTestCase(object):

    def setup(self):

        self.local_data_dir = os.path.join(os.path.dirname(__file__), 'data')
        self.web_data_dir = 'https://raw.githubusercontent.com/Small-Bodies-Node/pds4_tools/master/pds4_tools/tests/data/'

    def data(self, filename, from_web=False):

        if from_web:
            path_join_func = urljoin
            data_dir = self.web_data_dir

        else:
            path_join_func = os.path.join
            data_dir = self.local_data_dir

        return path_join_func(data_dir, filename)
