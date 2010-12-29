import sys
import symbol
from ast import NodeVisitor

class Semantics(NodeVisitor):
    """ An AST visitor class to display the tree
    """
    def __init__(self, buf=sys.stdout):
        self.buf = buf
        self.depth = 0
        self.sym = symbol.Symbol()

    def down(self, tag):
        if tag: self.sym.begin_scope(tag)

    def up(self, tag):
        if tag: self.sym.end_scope()

    # Program ============================================

    def visit_program(self, node):
        return 'program'
    
    # Variable declarations ===============================

    def visit_vardecls(self, node):
        pass

    def visit_vardecl(self, node):
        #        self.sym.insert(node.name)
        pass

    # Procedure declarations ==============================

    def visit_procdecls(self, node):
        pass

    def visit_procdecl(self, node):
        return 'procdecl'
    
    # Formals =============================================
    
    def visit_formals(self, node):
        pass

    def visit_param(self, node):
        pass

    # Statements ==========================================

    def visit_skip(self, node):
        pass

    def visit_pcall(self, node):
        return ' '

    def visit_ass(self, node):
        return ' '

    def visit_in(self, node):
        return ' '

    def visit_out(self, node):
        return ' '

    def visit_if(self, node):
        return ' '

    def visit_while(self, node):
        return ' '

    def visit_for(self, node):
        return ' '

    def visit_on(self, node):
        return ' '

    def visit_connect(self, node):
        return ' '

    def visit_aliases(self, node):
        return ' '

    def visit_return(self, node):
        return ' '

    def visit_seq(self, node):
        return ' '

    def visit_par(self, node):
        return ' '

    # Expressions =========================================

    def visit_exprlist(self, node):
        return '.'

    def visit_single(self, node):
        return '.'

    def visit_unary(self, node):
        return ' '

    def visit_binop(self, node):
        return ' '
    
    # Elements= ===========================================

    def visit_group(self, node):
        return '.'

    def visit_sub(self, node):
        return '.'

    def visit_fcall(self, node):
        return '.'

    def visit_number(self, node):
        return '.'

    def visit_boolean(self, node):
        return '.'

    def visit_string(self, node):
        return '.'

    def visit_char(self, node):
        return '.'

    def visit_id(self, node):
        return '.'

