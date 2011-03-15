# Copyright (c) 2011, James Hanlon, All rights reserved
# This software is freely distributable under a derivative of the
# University of Illinois/NCSA Open Source License posted in
# LICENSE.txt and at <http://github.xcore.com/>

import sys

class Error(object):
    """ A class for reporting errors and warnings during compilation """
    def __init__(self):
        self.num_errors = 0
        self.num_warnings = 0

    def report_error(self, msg, coord=None):
        if coord:
            print('{}: error: {}'.format(coord, msg), file=sys.stderr)
        else:
            print('Error: '+msg, file=sys.stderr)
        self.num_errors += 1

    def report_warning(self, msg, coord=None):
        if coord:
            print('{}: warning: {}'.format(coord, msg), file=sys.stderr)
        else:
            print('Warning: '+msg, file=sys.stderr)
        self.num_warnings += 1

    def fatal(self, msg):
            print('Fatal error: '+msg, file=sys.stderr)

    def any(self):
        return self.num_errors > 0

    def summary(self):
        return '{} errors and {} warnings'.format(
                self.num_errors, self.num_warnings)
