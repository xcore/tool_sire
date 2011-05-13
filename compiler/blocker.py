# Copyright (c) 2011, James Hanlon, All rights reserved
# This software is freely distributable under a derivative of the
# University of Illinois/NCSA Open Source License posted in
# LICENSE.txt and at <http://github.xcore.com/>

INDENT      = '  '
MAX_TEMPS   = 100
BEGIN_BLOCK = '^'
END_BLOCK   = '*'

class Blocker(object):
    """ 
    A class to buffer c-style blocks containing sequences of statements. Also
    allows temporary variables to be allocated in blocks.
    """
    class BlockBegin(object):
        def __init__(self):
            self.temps = []

    class BlockEnd(object):
        def __init__(self):
            pass

    def __init__(self, translator, buf):
        self.translator = translator
        self.buf = buf
        self.stack = []
        self.temps = []
        self.temp_counter = 0
        self.unused_temps = list(range(MAX_TEMPS))

    def begin(self):
        self.stack.append(self.BlockBegin())
        self.temps.append(BEGIN_BLOCK)

    def end(self):
        self.stack.append(self.BlockEnd())

        # Remove temps not out of scope
        while not self.temps[-1] == BEGIN_BLOCK:
           t = self.temps.pop()
           self.unused_temps.insert(0, t)
        self.temps.pop()

    def get_tmp(self):
        """
        Get the next unused temporary variable.
        """
        t = self.unused_temps[0]
        del self.unused_temps[0]
        self.temps.append(t)
        
        # Insert in in the current scope, skipping any nested blocks
        skip = 0
        for x in reversed(self.stack):
            if isinstance(x, self.BlockEnd):
                skip += 1
            if isinstance(x, self.BlockBegin):
                if skip == 0:
                    x.temps.append(t)
                    break
                else:
                    skip -= 1

        return '_t{}'.format(t)

    def insert(self, s):
        """
        Insert a statement.
        """
        self.stack.append(s)
   
    def output(self):
        depth = 0
        for x in self.stack:
            if isinstance(x, self.BlockBegin):
                self.out(depth, '{\n')
                depth += 1
                # Output temporaries declaration
                if len(x.temps) > 0: 
                    self.out(depth, 'unsigned '+
                        (', '.join(['_t{}'.format(t) for t in x.temps]))+';\n')
            elif isinstance(x, self.BlockEnd):
                depth -= 1
                self.out(depth, '}\n')
            else:
                self.out(depth, x+'\n')

    def out(self, d, s):
        """
        Write an indented line.
        """
        self.buf.write((INDENT*d)+s)
   

