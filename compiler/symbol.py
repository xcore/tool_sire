# Copyright (c) 2011, James Hanlon, All rights reserved
# This software is freely distributable under a derivative of the
# University of Illinois/NCSA Open Source License posted in
# LICENSE.txt and at <http://github.xcore.com/>

import sys

import definitions as defs
from type import Type

scopes = ['system', 'module', 'proc', 'func']

class SymbolTable(object):
    """ Symbol table.
    """
    def __init__(self, error, debug=False):
        self.error = error
        self.debug = debug
        self.scope = []
        self.tab = {}

    def begin_scope(self, tag):
        """ Begin a new scope.
        """
        s = ScopeTag(tag)
        self.scope.append(s)
        self.curr_scope = tag
        if(self.debug): 
            print("New scope '{}'".format(s.name))

    def unused_warning(self, name, coord):
        """ 
        Unused variable warning
        """
        self.error.report_warning(
                "variable '{}' declared but not used"
                .format(name), coord)

    def end_scope(self):
        """ End a scope.
        """
        s = None
        while not (self.scope[-1].type.isTag()):
            s = self.scope.pop()
            #del self.tab[s.name]
            if(self.debug): 
                print("Popped sym '{}' with type {}".format(s.name, s.type))

            # If symbol hasn't been used, give a warning
            if not s.mark and not s.name == defs.LABEL_MAIN:
                self.unused_warning(s.name, s.coord)
        
        s = self.scope.pop()
        self.curr_scope = self.get_curr_scope()
        if(self.debug): 
            print("Ended scope '{}', new scope '{}'"
                .format(s.name, self.curr_scope))
   
    def get_curr_scope(self):
        """ Traverse scope stack from top to bottom to find first scope tag.
        """
        for x in reversed(self.scope):
            if x.type.isTag():
                return x.name

    def insert_(self, name, type, expr, coord):
        """ Insert a new symbol in the table.
        """
        self.tab[name] = Symbol(name, type, expr, coord, self.scope[-1])
        self.scope.append(self.tab[name])
        if(self.debug):
            print("Inserted sym '{}' {} in scope '{}'"
                    .format(name, type, self.curr_scope))

    def insert(self, name, type, expr=None, coord=None):
        """ Insert a new symbol in the table if it doesn't already exist in the
            current scope.
        """
        if not self.lookup_scoped(name):
            self.insert_(name, type, expr, coord)
            return True
        return False

    # TODO: ideally, symbol lookup should be O(1) by creating new tables for
    # each new scope
    def lookup(self, key):
        """ Lookup a symbol in scope order.
        """
        symbol = None
        for x in reversed(self.scope):
            if x.name == key: 
                symbol = x
                break
        #if self.debug:
        #    print('Lookup: '+key+' found {}'.format(symbol))
        return symbol

    def lookup_scoped(self, key):
        """ Lookup a symbol in the current scope.
        """
        for x in reversed(self.scope):
            if x.type.isTag(): return None
            if x.name == key: return x

    def check_decl(self, key):
        """ Check a symbol has been declared.
        """
        s = self.lookup(key) 
        #print("check decl: "+key+" is {}".format(not s == None))
        return not s == None

    def check_form(self, key, forms):
        """ Check a symbol has been declared with the correct form.
        """
        if key in self.tab:
            return any(x == self.tab[key].type.form for x in forms)
        return False

    def check_type(self, key, types):
        """ Check a symbol has been declared with the correct form.
        """
        if key in self.tab:
            return any(x == self.tab[key].type for x in types)
        return False

    def mark_decl(self, key):
        """ Mark the first symbol.
        """
        for x in reversed(self.scope):
            if x.name == key:
                x.mark = True
                break;

    def dump(self, buf=sys.stdout):
        """ Dump the contents of the table to buf.
        """
        for x in self.scope:
            buf.write(repr(x))


class Symbol(object):
    """ A generic symbol with a name, type and scope.
    """
    def __init__(self, name, type, expr=None, coord=None, scope=None):
        self.name = name
        self.type = type
        self.expr = expr
        self.coord = coord
        self.scope = scope
        self.mark = False

    def __repr__(self):
        return '{}: {}'.format(self.name, self.type)


class ScopeTag(Symbol):
    """ A scope tag symbol.
    """
    def __init__(self, name):
        super(ScopeTag, self).__init__(name, Type('tag'), None, None, '')

