# Generic AST node class
class Node:
    def __init__(self, lineno=0, coloff=0, feilds=None, children=None):
        self.lineno = lineno
        self.coloff = coloff
        self.feilds = feilds
        if children:
             self.children = children
        else:
             self.children = [ ]

class Program(Node):
    def __init__(self, lineno=0, coloff=0, feilds=None, children=None):
        super(Program, self).__init__(self, lineno, coloff, fields, children)

class VarDecls(Node):

#class NodeVisitor(object):
#    
#    def visit(self, node):
#        'Visit a node.'
#        pass
#
#    def generic_visit(self, node):
#        'Called if no explicit visitor function exists for a node'
#        for field, value in iter_fields(node):
#            if isinstance(value, list):
#                for item in value:
#                    if isinstance(item, AST):
#                        self.visit(item)
#                    elif isinstance(value, AST):
#                        self.visit(value)
#
#class NodeTranslator(NodeVisitor):
#    
#    def generic_visit(self, node):
#        return node
#
#def dump(node):
#    pass
#
#def walk(node):
#    pass
