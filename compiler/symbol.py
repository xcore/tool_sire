class Symbol(object):
    """ Symbol table """
    def __init__(self):
        self.scope = []
        self.tab = []

    def begin_scope(self, tag):
        self.scope.append(tag)

    def end_scope(self):
        self.scope.pop()
    
    def insert(self, sym):
        pass

    def lookup(self, key):
        pass

    def lookup_scoped(self, key):
        pass
