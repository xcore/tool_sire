import sys
from ast import NodeVisitor

class Show(NodeVisitor):
    """ An AST visitor class to display the tree
    """
    def __init__(self, buf=sys.stdout, attrnames=False, showcoord=False):
        self.buf = buf
        self.attrnames = attrnames
        self.showcoord = showcoord

    # Program ============================================

    def visit_program(self, node):
        print "program at %s" % (node.coord)
    
    # Variable declarations ===============================

    def visit_vardecls(self, node):
        pass

    def visit_vardecl(self, node):
        print "vardecl"

    # Procedure declarations ==============================

    def visit_procdecls(self, node):
        pass

    def visit_procdecl(self, node):
        print "procdecl"
    
    # Formals =============================================
    
    def visit_formals(self, node):
        pass

    def visit_param(self, node):
        print "param"

    # Statements ==========================================

    def visit_skip(self, node):
        print "stmt"

    def visit_pcall(self, node):
        print "stmt"

    def visit_ass(self, node):
        print "stmt"

    def visit_in(self, node):
        print "stmt"

    def visit_out(self, node):
        print "stmt"

    def visit_if(self, node):
        print "stmt"

    def visit_while(self, node):
        print "stmt"

    def visit_for(self, node):
        print "stmt"

    def visit_on(self, node):
        print "stmt"

    def visit_connect(self, node):
        print "stmt"

    def visit_aliases(self, node):
        print "stmt"

    def visit_return(self, node):
        print "stmt"

    def visit_seq(self, node):
        print "stmt"

    def visit_par(self, node):
        print "stmt"

    # Expressions =========================================

    def visit_exprlist(self, node):
        print "stmt"

    def visit_unary(stmt, node):
        print "expr"

    def visit_binop(stmt, node):
        print "expr"
    
    # Elements= ===========================================

    def visit_group(stmt, node):
        print "elem"

    def visit_sub(stmt, node):
        print "elem"

    def visit_fncall(stmt, node):
        print "elem"

    def visit_number(stmt, node):
        print "elem"

    def visit_boolean(stmt, node):
        print "elem"

    def visit_string(stmt, node):
        print "elem"

    def visit_char(stmt, node):
        print "elem"

    def visit_id(stmt, node):
        print "elem"

