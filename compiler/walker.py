import ast
import util

class NodeWalker(object):
    """ A base class for walking an AST """  

    def decl(self, node):
        f = getattr(self, '{}'.format(util.camel_to_under(node.__class__.__name__)))
        return f(node)
    
    def defn(self, node, d):
        f = getattr(self, '{}'.format(util.camel_to_under(node.__class__.__name__)))
        return f(node, d)
    
    def param(self, node):
        f = getattr(self, '{}'.format(util.camel_to_under(node.__class__.__name__)))
        return f(node)
    
    def stmt(self, node, d):
        f = getattr(self, '{}'.format(util.camel_to_under(node.__class__.__name__)))
        return f(node, d)
    
    def expr(self, node):
        f = getattr(self, '{}'.format(util.camel_to_under(node.__class__.__name__)))
        return f(node)

    def elem(self, node):
        f = getattr(self, '{}'.format(util.camel_to_under(node.__class__.__name__)))
        return f(node)

