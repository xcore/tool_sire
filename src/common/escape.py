import sys

class Escape(Exception):
    """ An exception to cause a compiler stage to halt the process
    """
    def __init__(self, value):
        self.value = value

    def __str__(self):
        return repr(self.value)

