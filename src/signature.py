# Copyright (c) 2011, James Hanlon, All rights reserved
# This software is freely distributable under a derivative of the
# University of Illinois/NCSA Open Source License posted in
# LICENSE.txt and at <http://github.xcore.com/>

import sys

import definitions as defs
from type import Type
import semantics

# Valid types that can be taken by each formal type
param_conversions = {
    Type('var',     'single') : 
        [Type('var',  'single'), Type('var', 'sub')],

    Type('val',     'single') : 
        [Type('var',  'single'), Type('val', 'single'), Type('var', 'sub')],

    Type('var',     'alias')  :
        [Type('var',  'array'),  Type('var',  'alias')],

    Type('chanend', 'single') :
        [Type('chan', 'single'), Type('chan', 'sub')],
}

class SignatureTable(object):
    """ A procedure signature table """
    def __init__(self, semantics, debug=False):
        self.sem = semantics
        self.debug = debug
        self.tab = {}

    def insert(self, type, node):
        """ Insert a procedure signature """
        if (node.formals.params 
                and len(node.formals.params) > defs.MAX_PROC_PARAMETERS):
            return False

        self.tab[node.name] = Signature(node.name, type, node.formals.params)
        if(self.debug):
            print("Inserted sig for '{}' ({})".format(node.name, type))
        return True

    def lookup_param_type(self, name, i):
        return self.tab[name].params[i].type

    def lookup_array_qualifier(self, name, i):
        """ Given the index of an array parameter, return the index of the
            qualifying paramemer in the ordered set of formals.
        """
        params = self.tab[name].params
        assert(params[i].type == Type('var', 'alias'))
        qualifier = params[i].expr.elem.name
        for (i, x) in enumerate(params):
            if x.name == qualifier: return i
        return None

    def check_args(self, type, node):
        """ Check if a procedure signature is defined """
        if not node.name in self.tab:
            return False

        # Compare each param type to the type of each expr argument
        if self.debug:
            print('Checking args for {}'.format(node.name))

        # If there are no parameters, we don't need to check
        if not self.tab[node.name].params:
            return True

        # Otherwise check them
        for (x, y) in zip(self.tab[node.name].params, node.args.expr):
            t = self.sem.get_expr_type(y)
            if(self.debug):
                print('Arg type: {}'.format(t))
                print('Param type: {}'.format(x.type))

            # If argument y has no type, i.e. not defined
            if not t:
                return False

            # Check it against each valid conversion
            if not any(t==z for z in param_conversions[x.type]):
                return False
        
        return True
    
    def dump(self, buf=sys.stdout):
        """ Dump the contents of the table to buf """
        for x in self.scope:
            buf.write(repr(x))


class Signature(object):
    """ A procedure signature """
    def __init__(self, name, type, params):
        self.name = name
        self.type = type
        self.params = params

    def __repr__(self):
        return '{} {} {}'.format(self.name, self.type, ', '.join(
            [x.type for x in self.params]))

