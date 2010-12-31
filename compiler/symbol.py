import sys
import semantics

scopes = ['system', 'module', 'proc', 'func']

class SymbolTable(object):
    """ Symbol table
    """
    def __init__(self, semantics):
        self.semantics = semantics
        self.scope = []
        self.tab = {}

    def begin_scope(self, tag):
        """ Begin a new scope """
        s = ScopeTag(tag)
        self.scope.append(s)
        self.curr_scope = tag
        print('new scope {}'.format(tag))

    def end_scope(self):
        """ End a scope """
        while self.scope[-1].type != 'tag':
            s = self.scope.pop()
            if not s.mark:
                semantics.unused_warning(s.name, s.coord) 
        self.curr_scope = get_curr_scope()
        print('end scope')
   
    def get_curr_scope(self):
        """ Traverse scope stack from top to bottom to find first scope tag """
        for x in reversed(self.scope):
            if x.type == 'tag':
                self.curr_scope = x.type
                break
        return

    def insert_(self, name, type, coord):
        """ Insert a new symbol in the table """
        self.tab[name] = Symbol(name, type, coord, self.scope[-1])
        self.scope.append(self.tab[name])

    def insert(self, name, type, coord):
        """ Insert a new symbol in the table if it doesn't already exisit in the
            current scope """
        if not self.lookup_scoped(name):
            self.insert_(name, type, coord)
            return True
        else:
            return False

    def lookup(self, key):
        """ Lookup a symbol in any scope """
        return self.tab[key]

    def lookup_scoped(self, key):
        """ Lookup a symbol in the current scope """
        for x in reversed(self.scope):
            if x.type == 'tag': return None
            if x.name == key: return x

    def check_decl(self, key, *forms):
        """ Check if a symbol has been declared """
        if self.tab[key]:
            for x in forms:
                if x == self.tab[key].form:
                    return True
        return False

    def mark_decl(self, key):
        """ Mark a symbol """
        self.tab[key].mark = True

    def check_type(self, key, *types):
        """ Check if a symbol is of a specific type """
        if self.tab[key]:
            for x in types:
                if x == self.tab[key].type:
                    return True
        return False

    def dump(self, buf=sys.stdout):
        """ Dump the contents of the table to buf """
        for x in self.scope:
            buf.write(repr(x))


class Symbol(object):
    def __init__(self, name, type, coord, scope):
        self.name = name
        self.type = type
        self.coord = coord
        self.scope = scope
        self.mark = False

    def __repr__(self):
        return '{}: {}'.format(self.name, self.type)


class ScopeTag(Symbol):
    def __init__(self, name):
        self.name = name
        self.type = 'tag'
