import sys
import symbol
import signature
from ast import NodeVisitor

class Semantics(NodeVisitor):
    """ An AST visitor class to check the semantics of a sire program """
    def __init__(self, buf=sys.stdout):
        self.buf = buf
        self.depth = 0
        self.sym = symbol.Symbol()
        self.sig = signature.Signature()

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
        self.sym.insert("var", node.name)

    def visit_decl_array(self, node):
        self.sym.insert("array", node.name)

    def visit_decl_val(self, node):
        self.sym.insert("val", node.name)

    def visit_decl_port(self, node):
        self.sym.insert("port", node.name)

    # Procedure declarations ==============================

    def visit_proc_decls(self, node):
        pass

    def visit_decl_proc(self, node):
        self.sig.insert("proc", node)
        return 'proc'
    
    def visit_decl_func(self, node):
        self.sig.insert("func", node)
        return 'func'
    
    # Formals =============================================
    
    def visit_formals(self, node):
        pass

    def visit_param_var(self, node):
        self.sym.insert("var", node.name)

    def visit_param_alias(self, node):
        self.sym.insert("array", node.name)

    def visit_param_val(self, node):
        self.sym.insert("val", node.name)

    def visit_param_chanend(self, node):
        self.sym.insert("chanend", node.name)

    # Statements ==========================================

    def visit_stmt_skip(self, node):
        pass

    def visit_stmt_pcall(self, node):
        self.sig.check_def('proc', node)

    def visit_stmt_ass(self, node):
        self.sym.check_type(node.left, ('var'))

    def visit_stmt_in(self, node):
        self.sym.check_type(node.left, ('chanend', 'port'))

    def visit_stmt_out(self, node):
        self.sym.check_type(node.left, ('chanend', 'port'))

    def visit_stmt_if(self, node):
        pass

    def visit_stmt_while(self, node):
        pass

    def visit_stmt_for(self, node):
        pass

    def visit_stmt_on(self, node):
        self.sym.check_type(node.core, ('core'))

    def visit_stmt_connect(self, node):
        self.sym.check_type(node.core, ('core'))

    def visit_stmt_aliases(self, node):
        self.sym.check_type(node.name, ('alias'))

    def visit_stmt_return(self, node):
        pass

    def visit_stmt_seq(self, node):
        pass

    def visit_stmt_par(self, node):
        pass

    # Expressions =========================================

    def visit_expr_list(self, node):
        pass

    def visit_expr_single(self, node):
        pass

    def visit_expr_unary(self, node):
        pass

    def visit_expr_binop(self, node):
        pass
    
    # Elements= ===========================================

    def visit_elem_group(self, node):
        pass

    def visit_elem_sub(self, node):
        self.sym.check_def(node.name)

    def visit_elem_fcall(self, node):
        self.sig.check_def("func", node)

    def visit_elem_number(self, node):
        pass

    def visit_elem_boolean(self, node):
        pass

    def visit_elem_string(self, node):
        pass

    def visit_elem_char(self, node):
        pass

    def visit_elem_id(self, node):
        self.sym.check_def(node.value)

