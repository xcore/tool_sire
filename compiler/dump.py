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

    def visit_var_decls(self, node):
        self.out(node)

    def visit_decl_var(self, node):
        self.out(node)

    def visit_decl_array(self, node):
        self.out(node)

    def visit_decl_val(self, node):
        self.out(node)

    def visit_decl_port(self, node):
        self.out(node)

    # Procedure declarations ==============================

    def visit_proc_decls(self, node):
        self.out(node)
            
    def visit_decl_proc(self, node):
        self.out(node)
    
    def visit_decl_func(self, node):
        self.out(node)
    
    # Formals =============================================
    
    def visit_formals(self, node):
        self.out(node)
        
    def visit_param_var(self, node):
        self.out(node)

    def visit_param_alias(self, node):
        self.out(node)

    def visit_param_val(self, node):
        self.out(node)

    def visit_param_chanend(self, node):
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

    def visit_stmt_connect(self, node):
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

