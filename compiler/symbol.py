class Symbol(object):
    """ Symbol table """
    def __init__(self):
        self.scope = []
        self.tab = []

    def begin_scope(self, tag):
        self.scope.append(tag)

    def end_scope(self):
        self.scope.pop()
    
    def insert(self, type, sym):
        pass

    def lookup(self, key):
        pass

    def lookup_scoped(self, key):
        pass

    def check_def(self, key):
        """ Check a symbol is defined """
        pass
    
    def check_type(self, key, *types):
        """ Check a symbol is defined """
        pass
