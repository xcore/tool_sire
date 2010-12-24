import sys
import collections
from ast import NodeVisitor

class Show(NodeVisitor):
    """ An AST visitor class to display the tree
    """
    def __init__(self, buf=sys.stdout):
        self.buf = buf
        self.depth = 0
        self.scope = []

    def down(self, end):
        self.depth += 1
#        if isinstance(end, collections.Iterable):
#            for x in end:
#                self.scope.append(x)
#        else:
        self.scope.append(end)

    def up(self):
        self.depth -= 1
        end = self.scope.pop()
        self.buf.write(end)

    def out(self, s, indent=False):
        lead = '  ' * self.depth if indent else ''
        self.buf.write(lead + s)

    # Program ============================================

    def visit_program(self, node):
        self.out('program\n')
        return '\n'
    
    # Variable declarations ===============================

    def visit_vardecls(self, node):
        return ''

    def visit_vardecl(self, node):
        self.out('vardecl', True)
        return '\n'

    # Procedure declarations ==============================

    def visit_procdecls(self, node):
        return '.'

    def visit_procdecl(self, node):
        self.buf.write('\n')
        self.out("procdecl (", True)
        return '\n'
    
    # Formals =============================================
    
    def visit_formals(self, node):
        return ') is\n'

    def visit_param(self, node):
        self.out('param')
        return '.'

    # Statements ==========================================

    def visit_skip(self, node):
        self.buf.write('\n')
        self.out('skip', True)
        return ' '

    def visit_pcall(self, node):
        self.buf.write('\n')
        self.out('pcall', True)
        return ' '

    def visit_ass(self, node):
        self.buf.write('\n')
        self.out('ass', True)
        return ' '

    def visit_in(self, node):
        self.buf.write('\n')
        self.out('in', True)
        return ' '

    def visit_out(self, node):
        self.buf.write('\n')
        self.out('out', True)
        return ' '

    def visit_if(self, node):
        self.buf.write('\n')
        self.out('if', True)
        return ' '

    def visit_while(self, node):
        self.buf.write('\n')
        self.out('while', True)
        return ' '

    def visit_for(self, node):
        self.buf.write('\n')
        self.out('for', True)
        return ' '

    def visit_on(self, node):
        self.buf.write('\n')
        self.out('on', True)
        return ' '

    def visit_connect(self, node):
        self.buf.write('\n')
        self.out('connect', True)
        return ' '

    def visit_aliases(self, node):
        self.buf.write('\n')
        self.out('aliases', True)
        return ' '

    def visit_return(self, node):
        self.buf.write('\n')
        self.out('return', True)
        return ' '

    def visit_seq(self, node):
        #self.buf.write('\n')
        self.out('{', True)
        lead = '  ' * self.depth
        return '\n' + lead + '}'

    def visit_par(self, node):
        #self.buf.write('\n')
        self.out('{', True)
        lead = '  ' * self.depth
        return '\n' + lead + '}'

    # Expressions =========================================

    def visit_exprlist(self, node):
        return '.'

    def visit_unary(self, node):
        self.out('expr')
        return '.'

    def visit_binop(self, node):
        self.out('expr')
        return '.'
    
    # Elements= ===========================================

    def visit_group(self, node):
        self.out('elem')
        return '.'

    def visit_sub(self, node):
        self.out('elem')
        return '.'

    def visit_fcall(self, node):
        self.out('elem')
        return '.'

    def visit_number(self, node):
        self.out('elem')
        return '.'

    def visit_boolean(self, node):
        self.out('elem')
        return '.'

    def visit_string(self, node):
        self.out('elem')
        return '.'

    def visit_char(self, node):
        self.out('elem')
        return '.'

    def visit_id(self, node):
        self.out('elem')
        return '.'

