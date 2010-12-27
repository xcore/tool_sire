import sys
import collections
from ast import NodeVisitor

class Dump(NodeVisitor):
    """ An AST visitor class to display the tree
    """
    def __init__(self, buf=sys.stdout):
        self.buf = buf
        self.depth = 0

    def down(self):
        self.depth += 1

    def up(self):
        self.depth -= 1

    def out(self, s):
        lead = '  ' * self.depth
        self.buf.write(lead + s + '\n')

    # Program ============================================

    def visit_program(self, node):
        self.out('program')
    
    # Variable declarations ===============================

    def visit_vardecls(self, node):
        pass

    def visit_vardecl(self, node):
        self.out('vardecl')

    # Procedure declarations ==============================

    def visit_procdecls(self, node):
        pass
            
    def visit_procdecl(self, node):
        self.out("procdecl")
    
    # Formals =============================================
    
    def visit_formals(self, node):
        pass
        
    def visit_param(self, node):
        self.out('param')

    # Statements ==========================================

    def visit_skip(self, node):
        self.out('skip')

    def visit_pcall(self, node):
        self.out('pcall')

    def visit_ass(self, node):
        self.out('ass')

    def visit_in(self, node):
        self.out('in')

    def visit_out(self, node):
        self.out('out')

    def visit_if(self, node):
        self.out('if')

    def visit_while(self, node):
        self.out('while')

    def visit_for(self, node):
        self.out('for')

    def visit_on(self, node):
        self.out('on')

    def visit_connect(self, node):
        self.out('connect')

    def visit_aliases(self, node):
        self.out('aliases')

    def visit_return(self, node):
        self.out('return')

    def visit_seq(self, node):
        self.out('seq')

    def visit_par(self, node):
        self.out('par')

    # Expressions =========================================

    def visit_exprlist(self, node):
        pass

    def visit_single(self, node):
        self.out('expr')

    def visit_unary(self, node):
        self.out('expr')

    def visit_binop(self, node):
        self.out('expr')
    
    # Elements= ===========================================

    def visit_group(self, node):
        self.out('elem')

    def visit_sub(self, node):
        self.out('elem')

    def visit_fcall(self, node):
        self.out('elem')

    def visit_number(self, node):
        self.out('elem')

    def visit_boolean(self, node):
        self.out('elem')

    def visit_string(self, node):
        self.out('elem')

    def visit_char(self, node):
        self.out('elem')

    def visit_id(self, node):
        self.out('elem')

