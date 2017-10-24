# Script outside of pds4_tools package to be used for building
# PDS4 Viewer as a stand-alone application, or easy start-up
# by user.

from pds4_tools import viewer

if __name__ == '__main__':
    viewer.core.main()
