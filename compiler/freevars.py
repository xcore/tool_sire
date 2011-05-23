# Copyright (c) 2011, James Hanlon, All rights reserved
# This software is freely distributable under a derivative of the
# University of Illinois/NCSA Open Source License posted in
# LICENSE.txt and at <http://github.xcore.com/>

from walker import NodeWalker

# TODO: return set based on preference.

class FreeVars(NodeWalker):
    """
    Calculate the set of free variables within a statement. This can be:
     - All definitions and uses.
     - All definitions.
     - All uses and definitions of array types only.
    """
    def __init__(self):
        pass

    def allvars(self, node):
        self.collect = 'all'
        return self.stmt(node)

    def defs(self, node):
        self.collect = 'defs'
        return self.stmt(node)

    def arrays(self, node):
        self.collect = 'array'
        return self.stmt(node)

    # Statements ==========================================

    def stmt_seq(self, node):
        c = set()
        [c.update(self.stmt(x)) for x in node.stmt]
        return c

    def stmt_par(self, node):
        c = set()
        [c.update(self.stmt(x)) for x in node.stmt]
        return c

    def stmt_skip(self, node):
        return set()

    def stmt_pcall(self, node):
        c = set()
        [c.update(self.expr(x)) for x in node.args]
        return c

    def stmt_ass(self, node):
        c = self.elem(node.left)
        c |= self.expr(node.expr)
        return c

    def stmt_alias(self, node):
        return self.elem(node.slice)

    def stmt_if(self, node):
        c = self.expr(node.cond)
        c |= self.stmt(node.thenstmt)
        c |= self.stmt(node.elsestmt)
        return c

    def stmt_while(self, node):
        c = self.expr(node.cond)
        c |= self.stmt(node.stmt)
        return c

    def stmt_for(self, node):
        c = self.elem(node.var)
        c |= self.expr(node.init)
        c |= self.expr(node.bound)
        c |= self.expr(node.step)
        c |= self.stmt(node.stmt)
        return c

    def stmt_rep(self, node):
        c = self.elem(node.var)
        c |= self.expr(node.init)
        c |= self.expr(node.count)
        c |= self.stmt(node.stmt)
        return c

    def stmt_on(self, node):
        return self.elem(node.pcall)

    def stmt_return(self, node):
        return self.expr(node.expr)
    
    # Expressions =========================================

    def expr_single(self, node):
        return self.elem(node.elem)

    def expr_unary(self, node):
        return self.elem(node.elem)

    def expr_binop(self, node):
        c = self.elem(node.elem)
        c |= self.expr(node.right)
        return c
    
    # Elements= ===========================================

    # Identifier
    def elem_id(self, node):
        return set([node]) if self.include_singles else set()

    # Array subscript
    def elem_sub(self, node):
        c = self.expr(node.expr)
        return c | set([node])

    # Array slice
    def elem_slice(self, node):
        c = self.expr(node.begin)
        c |= self.expr(node.end)
        return c | set([node])

    def elem_group(self, node):
        return self.expr(node.expr)

    def elem_pcall(self, node):
        c = set()
        [c.update(self.expr(x)) for x in node.args]
        return c

    def elem_fcall(self, node):
        c = set()
        [c.update(self.expr(x)) for x in node.args]
        return c

    def elem_number(self, node):
        return set()

    def elem_boolean(self, node):
        return set()

    def elem_string(self, node):
        return set()

    def elem_char(self, node):
        return set()


