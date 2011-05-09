# Copyright (c) 2011, James Hanlon, All rights reserved
## This software is freely distributable under a derivative of the
## University of Illinois/NCSA Open Source License posted in
## LICENSE.txt and at <http://github.xcore.com/>

import sys
import collections

from ast import NodeVisitor

class Dump(NodeVisitor):
    """ An AST visitor class to display the tree
    """
    def __init__(self, buf=sys.stdout):
        self.buf = buf
        self.depth = 0

    def down(self, tag):
        self.depth += 1

    def up(self, tag):
        self.depth -= 1

    def out(self, node):
        lead = '  ' * self.depth
        self.buf.write(lead + repr(node) + '\n')

    # Program ============================================

    def visit_program(self, node):
        self.out(node)

    # Variable declarations ===============================

    def visit_decls(self, node):
        self.out(node)

    def visit_decl(self, node):
        self.out(node)

    # Procedure declarations ==============================

    def visit_defs(self, node):
        self.out(node)
            
    def visit_def(self, node):
        self.out(node)
    
    # Formals =============================================
    
    def visit_formals(self, node):
        self.out(node)
        
    def visit_param(self, node):
        self.out(node)

    # Statements ==========================================

    def visit_stmt_seq(self, node):
        self.out(node)

    def visit_stmt_par(self, node):
        self.out(node)

    def visit_stmt_skip(self, node):
        self.out(node)

    def visit_stmt_pcall(self, node):
        self.out(node)

    def visit_stmt_ass(self, node):
        self.out(node)

    def visit_stmt_in(self, node):
        self.out(node)

    def visit_stmt_out(self, node):
        self.out(node)

    def visit_stmt_if(self, node):
        self.out(node)

    def visit_stmt_while(self, node):
        self.out(node)

    def visit_stmt_for(self, node):
        self.out(node)

    def visit_stmt_on(self, node):
        self.out(node)

    def visit_stmt_aliases(self, node):
        self.out(node)

    def visit_stmt_return(self, node):
        self.out(node)

    # Expressions =========================================

    def visit_expr_list(self, node):
        self.out(node)

    def visit_expr_single(self, node):
        self.out(node)

    def visit_expr_unary(self, node):
        self.out(node)

    def visit_expr_binop(self, node):
        self.out(node)
    
    # Elements= ===========================================

    def visit_elem_group(self, node):
        self.out(node)

    def visit_elem_sub(self, node):
        self.out(node)

    def visit_elem_fcall(self, node):
        self.out(node)

    def visit_elem_number(self, node):
        self.out(node)

    def visit_elem_boolean(self, node):
        self.out(node)

    def visit_elem_string(self, node):
        self.out(node)

    def visit_elem_char(self, node):
        self.out(node)

    def visit_elem_id(self, node):
        self.out(node)

