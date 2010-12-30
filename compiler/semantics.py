import sys
import symbol
from ast import NodeVisitor

class Semantics(NodeVisitor):
    """ An AST visitor to check the semantics of sire
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

    def visit_var_decls(self, node):
        pass

    def visit_decl_var(self, node):
        # self.sym.insert(node.name)
        pass

    def visit_decl_array(self, node):
        pass

    def visit_decl_val(self, node):
        pass

    def visit_decl_port(self, node):
        pass

    # Procedure declarations ==============================

    def visit_proc_decls(self, node):
        pass

    def visit_decl_proc(self, node):
        return 'proc'
    
    def visit_decl_func(self, node):
        return 'func'
    
    # Formals =============================================
    
    def visit_formals(self, node):
        pass

    def visit_param_var(self, node):
        pass

    def visit_param_alias(self, node):
        pass

    def visit_param_val(self, node):
        pass

    def visit_param_port(self, node):
        pass

    # Statements ==========================================

    def visit_stmt_skip(self, node):
        pass

    def visit_stmt_pcall(self, node):
        return ' '

    def visit_stmt_ass(self, node):
        return ' '

    def visit_stmt_in(self, node):
        return ' '

    def visit_stmt_out(self, node):
        return ' '

    def visit_stmt_if(self, node):
        return ' '

    def visit_stmt_while(self, node):
        return ' '

    def visit_stmt_for(self, node):
        return ' '

    def visit_stmt_on(self, node):
        return ' '

    def visit_stmt_connect(self, node):
        return ' '

    def visit_stmt_aliases(self, node):
        return ' '

    def visit_stmt_return(self, node):
        return ' '

    def visit_stmt_seq(self, node):
        return ' '

    def visit_stmt_par(self, node):
        return ' '

    # Expressions =========================================

    def visit_expr_list(self, node):
        return '.'

    def visit_expr_single(self, node):
        return '.'

    def visit_expr_unary(self, node):
        return ' '

    def visit_expr_binop(self, node):
        return ' '
    
    # Elements= ===========================================

    def visit_elem_group(self, node):
        return '.'

    def visit_elem_sub(self, node):
        return '.'

    def visit_elem_fcall(self, node):
        return '.'

    def visit_elem_number(self, node):
        return '.'

    def visit_elem_boolean(self, node):
        return '.'

    def visit_elem_string(self, node):
        return '.'

    def visit_elem_char(self, node):
        return '.'

    def visit_elem_id(self, node):
        return '.'

