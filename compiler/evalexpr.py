# Copyright (c) 2011, James Hanlon, All rights reserved
# This software is freely distributable under a derivative of the
# University of Illinois/NCSA Open Source License posted in
# LICENSE.txt and at <http://github.xcore.com/>

import error
import ast
from walker import NodeWalker

class EvaluateExpr(NodeWalker):
    """
    Evaluate a constant-valued expression.
    """
    def __init__(self, sym, errorlog):
        self.sym = sym
        self.errorlog = errorlog

    def non_const_error(self, node):
        self.errorlog.report_error("non-constant '{}' in expr"
                .format(node.name), node.coord)

    # Expressions =========================================

    def expr_single(self, node):
        return self.elem(node.elem)

    def expr_unary(self, node):
        if node.op == '-':
            return -self.elem(node.elem)
        elif node.op == '~':
            return ~self.elem(node.elem)
        else:
            assert 0

    def expr_binop(self, node):
        if node.op == '+':
            return self.elem(node.elem) + self.expr(node.right)
        elif node.op == '-':
            return self.elem(node.elem) - self.expr(node.right)
        elif node.op == '*':
            return self.elem(node.elem) * self.expr(node.right)
        elif node.op == '/':
            return self.elem(node.elem) / self.expr(node.right)
        elif node.op == '%':
            return self.elem(node.elem) % self.expr(node.right)
        elif node.op == 'or':
            return self.elem(node.elem) | self.expr(node.right)
        elif node.op == 'and':
            return self.elem(node.elem) & self.expr(node.right)
        elif node.op == 'xor':
            return self.elem(node.elem) ^ self.expr(node.right)
        elif node.op == '<<':
            return self.elem(node.elem) << self.expr(node.right)
        elif node.op == '>>':
            return self.elem(node.elem) >> self.expr(node.right)
        elif node.op == '<':
            return self.elem(node.elem) < self.expr(node.right)
        elif node.op == '>':
            return self.elem(node.elem) > self.expr(node.right)
        elif node.op == '<=':
            return self.elem(node.elem) <= self.expr(node.right)
        elif node.op == '>=':
            return self.elem(node.elem) >= self.expr(node.right)
        elif node.op == '=':
            return self.elem(node.elem) == self.expr(node.right)
        elif node.op == '~=':
            return self.elem(node.elem) != self.expr(node.right)
        else:
            assert 0
    
    # Elements= ===========================================

    def elem_id(self, node):
        s = sym.lookup(node.name)
        if s and s.value:
            return s.value
        else:
            self.non_const_error(node)

    def elem_group(self, node):
        return self.expr(node.expr)

    def elem_number(self, node):
        return node.value

    def elem_boolean(self, node):
        return node.value

    def elem_char(self, node):
        return node.value
    
    # Disallowed
    
    def elem_fcall(self, node):
        self.non_const_error(node)

    def elem_sub(self, node):
        self.non_const_error(node)

    def elem_slice(self, node):
        self.non_const_error(node)

    def elem_index(self, node):
        self.non_const_error(node)

    def elem_string(self, node):
        self.non_const_error(node)
    

