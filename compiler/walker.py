# Copyright (c) 2011, James Hanlon, All rights reserved
# This software is freely distributable under a derivative of the
# University of Illinois/NCSA Open Source License posted in
# LICENSE.txt and at <http://github.xcore.com/>

import util

class NodeWalker(object):
    """
    A base class for walking an AST.
    """  

    def decl(self, node, d=None):
        f = getattr(self, '{}'.format(util.camel_to_under(node.__class__.__name__)))
        return f(node, d) if d else f(node)
    
    def defn(self, node, d=None):
        f = getattr(self, '{}'.format(util.camel_to_under(node.__class__.__name__)))
        return f(node, d) if d else f(node)
    
    def param(self, node):
        f = getattr(self, '{}'.format(util.camel_to_under(node.__class__.__name__)))
        return f(node)
    
    def stmt(self, node, d=None):
        f = getattr(self, '{}'.format(util.camel_to_under(node.__class__.__name__)))
        return f(node, d) if d else f(node)
    
    def expr(self, node):
        f = getattr(self, '{}'.format(util.camel_to_under(node.__class__.__name__)))
        return f(node)

    def elem(self, node):
        f = getattr(self, '{}'.format(util.camel_to_under(node.__class__.__name__)))
        return f(node)

