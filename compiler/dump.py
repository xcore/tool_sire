from ast import Node, NodeVisitor

class Dump(NodeVisitor):
    
    def visit_program(self, node):
        print "program at {0}:{1}".format(node.lineno, node.coloff)

    def visit_var_decl(self, node):
        print "vardecl at {0}:{1}".format(node.lineno, node.coloff)

    def visit_proc_decl(self, node):
        print "procdecl at {0}:{1}".format(node.lineno, node.coloff)

    def visit_param(self, node):
        print "param"

    def visit_stmt(self, node):
        print "stmt"

    def visit_expr(stmt, node):
        print "expr"

    def visit_elem(stmt, node):
        print "elem"
