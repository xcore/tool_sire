import sys
from type import Type
import semantics

# Valid types that can be taken by each formal type
param_conversions = {
    Type('var',     'single') : [Type('var',  'single'), Type('var', 'sub')],
    Type('val',     'single') : [Type('var',  'single'), 
        Type('val', 'single'), Type('var', 'sub')],
    Type('var',     'alias')  : [Type('var',  'array'),  Type('var',  'alias')],
    Type('chanend', 'single') : [Type('chan', 'single'), Type('chan', 'sub')],
}

class SignatureTable(object):
    """ A procedure signature table """
    def __init__(self, semantics, debug=False):
        self.sem = semantics
        self.debug = debug
        self.tab = {}

    def insert(self, type, node):
        """ Insert a procedure signature """
        self.tab[node.name] = Signature(node.name, type, node.formals.params)
        if(self.debug):
            print("Inserted sig for '{}' ({})".format(node.name, type))


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

