# Copyright (c) 2011, James Hanlon, All rights reserved
# This software is freely distributable under a derivative of the
# University of Illinois/NCSA Open Source License posted in
# LICENSE.txt and at <http://github.xcore.com/>

from walker import NodeWalker

class Context(NodeWalker):
    """
    An AST walker to determine the variable context of a statement. This
    recursively propagates identifiers for singles, array subscripts and array
    slices up the AST.
    """
    def __init__(self):
        pass

    # Program ============================================

    def walk_stmt(self, node):
        """
        Return a list of tuples: (name, type).
        """
        return self.stmt(node)

    # Statements ==========================================

    def stmt_seq(self, node):
        c = []
        [c.extend(self.stmt(x)) for x in node.stmt]
        return c

    def stmt_par(self, node):
        c = []
        [c.extend(self.stmt(x)) for x in node.stmt]
        return c

    def stmt_skip(self, node):
        return []

    def stmt_pcall(self, node):
        c = []
        [c.extend(self.expr(x)) for x in node.args]
        return c

    def stmt_ass(self, node):
        c = self.elem(node.left)
        c += self.expr(node.expr)
        return c

    def stmt_alias(self, node):
        return self.expr(node.slice)

    def stmt_if(self, node):
        c = self.expr(node.cond)
        c += self.stmt(node.thenstmt)
        c += self.stmt(node.elsestmt)
        return c

    def stmt_while(self, node):
        c = self.expr(node.cond)
        c += self.stmt(node.stmt)
        return c

    def stmt_for(self, node):
        c = self.elem(node.var)
        c += self.expr(node.init)
        c += self.expr(node.bound)
        c += self.expr(node.step)
        c += self.stmt(node.stmt)
        return c

    def stmt_rep(self, node):
        c = self.elem(node.var)
        c += self.expr(node.init)
        c += self.expr(node.count)
        c += self.elem(node.stmt)
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
        c += self.expr(node.right)
        return c
    
    # Elements= ===========================================

    def elem_group(self, node):
        return self.expr(node.expr)

    # Identifier
    def elem_id(self, node):
        return [node]

    # Array subscript
    def elem_sub(self, node):
        c = self.expr(node.expr)
        return c + [node]

    # Array slice
    def elem_slice(self, node):
        c = self.expr(node.begin)
        c += self.expr(node.end)
        return c + [node]

    def elem_pcall(self, node):
        c = []
        [c.extend(self.expr(x)) for x in node.args]
        return c

    def elem_fcall(self, node):
        c = []
        [c.extend(self.expr(x)) for x in node.args]
        return c

    def elem_number(self, node):
        return []

    def elem_boolean(self, node):
        return []

    def elem_string(self, node):
        return []

    def elem_char(self, node):
        return []

