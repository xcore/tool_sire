import sys
import ast
from ast import NodeVisitor

class Show(NodeVisitor):
    """ An AST visitor class to display the tree
    """
    def __init__(self, buf=sys.stdout):
        self.buf = buf
        self.depth = 0

    def down(self):
        self.depth += 1

    def up(self):
        self.depth -= 1

    def out(self, s, indent=False):
        lead = '  ' * self.depth if indent else ''
        self.buf.write(lead + s)

    # Program ============================================

    def visit_program(self, node):
        self.visit_vardecls(node.vardecls)
        self.visit_procdecls(node.procdecls)
    
    # Variable declarations ===============================

    def visit_vardecls(self, node):
        for v in node.children():
            self.visit_vardecl(v)
            self.buf.write('\n')

    def visit_vardecl(self, node):
        if node.form == "var":
            self.out('%s %s' % (node.type, self.elem(node.name)), True)
        elif node.form == "array":
            self.out('%s %s[%s]' % (node.type, self.elem(node.name), self.expr(node.expr)), True)
        elif node.form == "val":
            self.out('val %s := %s' % 
                (self.elem(node.name), self.expr(node.expr)), True)
        elif node.form == "port":
            self.out('port %s %s' % (self.elem(node.name), self.expr(node.expr)), True)
        else: raise Exception('Invalid variable declaration')

        # form, type, name
        #self.visit_expr(node.expr)

    # Procedure declarations ==============================

    def visit_procdecls(self, node):
        for p in node.children():
            #self.visit_procdecl(p)
            self.buf.write('\n')

    def visit_procdecl(self, node):
        self.out("procdecl", True)
        self.visit_formals(node.formals)
        self.visit_vardecls(node.formals)
        # type, name, stmt
        self.visit_stmt(node.stmt)
    
    # Formals =============================================
    
    def visit_formals(self, node):
        for p in node.children():
            self.visit_param(p)
            self.buf.write(', ')

    def visit_param(self, node):
        self.out('param')
        # type, name

    # Statements ==========================================

    # This should be implemented as double dispatch
    def stmt(self, node):
        if   isinstance(node, ast.Seq):     self.visit_seq(node)
        elif isinstance(node, ast.Par):     self.visit_par(node)
        elif isinstance(node, ast.Skip):    self.visit_skip(node)
        elif isinstance(node, ast.Pcall):   self.visit_pcall(node)
        elif isinstance(node, ast.Ass):     self.visit_ass(node)
        elif isinstance(node, ast.In):      self.visit_in(node)
        elif isinstance(node, ast.Out):     self.visit_out(node)
        elif isinstance(node, ast.If):      self.visit_if(node)
        elif isinstance(node, ast.While):   self.visit_while(node)
        elif isinstance(node, ast.For):     self.visit_for(node)
        elif isinstance(node, ast.On):      self.visit_on(node)
        elif isinstance(node, ast.Connect): self.visit_connect(node)
        elif isinstance(node, ast.Aliases): self.visit_aliases(node)
        elif isinstance(node, ast.Return):  self.visit_return(node)
        else: raise Exception('Invalid statement')

    def visit_seq(self, node):
        self.out('{', True)
        for s in node.children():
            print "stmt"
            self.buf.write('\n')
        self.out('}', True)

    def visit_par(self, node):
        self.out('{', True)
        for s in node.children():
            print "stmt"
            self.buf.write('\n')
        self.out('}', True)

    def visit_skip(self, node):
        self.out('skip', True)

    def visit_pcall(self, node):
        self.out('pcall', True)

    def visit_ass(self, node):
        self.out('ass', True)

    def visit_in(self, node):
        self.out('in', True)

    def visit_out(self, node):
        self.out('out', True)

    def visit_if(self, node):
        self.out('if', True)

    def visit_while(self, node):
        self.out('while', True)

    def visit_for(self, node):
        self.out('for', True)

    def visit_on(self, node):
        self.out('on', True)

    def visit_connect(self, node):
        self.out('connect', True)

    def visit_aliases(self, node):
        self.out('aliases', True)

    def visit_return(self, node):
        self.out('return', True)

    # Expressions =========================================

    def expr(self, node):
        if   isinstance(node, ast.ExprList): self.visit_exprlist(node)
        elif isinstance(node, ast.Unary): self.visit_unary(node)
        elif isinstance(node, ast.Binop): self.visit_binop(node)
        else: raise Exception('Invalid expression')

    def visit_exprlist(self, node):
        for e in node.children():
            self.visit_expr(node)
    
    def visit_unary(self, node):
        self.out('expr')

    def visit_binop(self, node):
        self.out('expr')
    
    # Elements= ===========================================

    def elem(self, node):
        if   isinstance(node, ast.Group):   self.visit_group(node)
        elif isinstance(node, ast.Sub):     self.visit_sub(node)
        elif isinstance(node, ast.Fcall):   self.visit_fcall(node)
        elif isinstance(node, ast.Number):  self.visit_number(node)
        elif isinstance(node, ast.Boolean): self.visit_boolean(node)
        elif isinstance(node, ast.String):  self.visit_string(node)
        elif isinstance(node, ast.Char):    self.visit_char(node)
        elif isinstance(node, ast.Id):      self.visit_id(node)
        else: raise Exception('Invalid element.')

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
        return node.value

