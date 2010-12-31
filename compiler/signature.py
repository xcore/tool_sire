import semantics

proc_types = ['proc', 'func']

class SignatureTab(object):
    def __init__(self, semantics):
        self.semantics = semantics
        self.tab = {}

    def insert(self, type, node):
        """ Insert a procedure signature """
        self.tab[node.name] = Signature(node.name, type node.formals.params)

    def check_def(self, type, node):
        """ Check if a procedure signature is defined """
        if not self.tab[name]:
            return False
        for x, y in zip(self.tab[name].params, node.args)
            if x.type != semantics.get_type(y)
                return False
        return True
    
    def dump(self, buf=sys.stdout):
        """ Dump the contents of the table to buf """
        for x in self.scope:
            buf.write(repr(x))


class Signature(object):
    """ A procedure signature """
    def __init__(self, name, type, *params):
        self.name = name
        self.type = type
        self.params = params

    def __repr__(self):
        return '{} {} {}'.format(self.name, self.type, ', '.join(
            [x.type for x in self.params]))

