# Copyright (c) 2011, James Hanlon, All rights reserved
# This software is freely distributable under a derivative of the
# University of Illinois/NCSA Open Source License posted in
# LICENSE.txt and at <http://github.xcore.com/>

import sys

import definitions as defs
from type import Type

class SignatureTable(object):
    """
    A procedure signature table.
    """
    def __init__(self, debug=False):
        self.debug = debug
        self.tab = {}
        self.mobile_proc_names = []
        self.id_count = 0

    def insert(self, type, node, mobile=True):
        """
        Insert a procedure signature, mobile denotes if it will be added to the
        jump table and be mobile between cores.
        """
        if (node.formals and len(node.formals) > defs.MAX_PROC_PARAMETERS):
            return False
        
        self.tab[node.name] = Signature(node.name, type, node.formals)
        
        if mobile:
            self.mobile_proc_names.append(node.name)
        
        if(self.debug):
            print("Inserted sig for '{}' ({})".format(node.name, type))
        
        return True

    def lookup_param_type(self, name, i):
        """
        Given a procedure name and an index, return the formal type.
        """
        return self.tab[name].params[i].type

    def lookup_array_qualifier(self, name, i):
        """ 
        Given the index of an array parameter, return the index of the
        qualifying paramemer in the ordered set of formal parameters.
        """
        params = self.tab[name].params
        assert(params[i].type == Type('ref', 'array')) 
        
        qualifier = params[i].expr.elem.name
        for (i, x) in enumerate(params):
            if x.name == qualifier: return i
        
        return None

    def get_params(self, name):
        """
        Return the list of formal parameter declarations for a named procedure.
        """
        if node.name in self.tab:
            return self.tab[node.name].params
        else:
            return None

    def add_mobile_proc(self, name):
        """
        Add a process to the list of mobiles.
        """
        self.mobile_proc_names.append(name)

    def unique_process_name(self):
        name = '_p{}'.format(self.id_count)
        self.id_count = self.id_count + 1
        return name

    def dump(self, buf=sys.stdout):
        """
        Dump the contents of the table to buf.
        """
        for x in self.scope:
            buf.write(repr(x))


class Signature(object):
    """
    A procedure signature.
    """
    def __init__(self, name, type, params):
        self.name = name
        self.type = type
        self.params = params

    def __repr__(self):
        return '{} {} {}'.format(self.name, self.type, ', '.join(
            [x.type for x in self.params]))

