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
            print('Error: {}'.format(msg), file=sys.stderr)
        self.num_errors += 1

    def report_warning(self, msg, coord=None):
        if coord:
            print('{}: warning: {}'.format(coord, msg), file=sys.stderr)
        else:
            print('Warning: {}'.format(msg), file=sys.stderr)
        self.num_warnings += 1

    def fatal(self):
        pass

    def summary(self):
        return '{} errors and {} warnings'.format(
                self.num_errors, self.num_warnings)