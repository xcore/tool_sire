import sys
import ast
from ast import NodeVisitor

class Show(object):
    """ An AST visitor class to display the tree
    """
    def __init__(self, buf=sys.stdout):
        self.buf = buf

    # Program ============================================

    def visit_program(self, node):
        self.vardecls(node.vardecls, 0)
        self.buf.write('\n')
        self.procdecls(node.procdecls, 0)
    
    # Variable declarations ===============================

    def vardecls(self, node, d):
        self.buf.write((';'+(' '*d)+'\n').
                join([self.vardecl(x) for x in node.children()]))
        if len(node.children())>0: self.buf.write(';\n')

    def vardecl(self, node):
        if node.form == "var":
            return '%s %s' % (node.type, self.elem(node.name))
        elif node.form == "array":
            return '%s %s[%s]' % (node.type, self.elem(node.name), 
                    self.expr(node.expr))
        elif node.form == "val":
            return 'val %s := %s' % (self.elem(node.name), 
                    self.expr(node.expr))
        elif node.form == "port":
            return 'port %s : %s' % (self.elem(node.name), 
                    self.expr(node.expr))
        else:
            raise Exception('Invalid variable declaration')

    # Procedure declarations ==============================

    def procdecls(self, node, d):
        for p in node.children():
            self.procdecl(p, d)
        pass

    def procdecl(self, node, d):
        self.buf.write('%s %s(%s) is\n' % (node.type, self.elem(node.name), 
                self.formals(node.formals)))
        self.vardecls(node.vardecls, d+1)
        self.stmt(node.stmt, d+1)
        self.buf.write('\n\n')
    
    # Formals =============================================
    
    def formals(self, node):
        return ', '.join([self.param(x) for x in node.children()])

    def param(self, node):
        # type, name
        return '%s %s' % (node.type, self.elem(node.name))

    # Statements ==========================================

    # This should be implemented as double dispatch
    def stmt(self, node, d):
        if   isinstance(node, ast.Seq):     return self.visit_seq(node, d)
        elif isinstance(node, ast.Par):     return self.visit_par(node, d)
        elif isinstance(node, ast.Skip):    return self.visit_skip(node, d)
        elif isinstance(node, ast.Pcall):   return self.visit_pcall(node, d)
        elif isinstance(node, ast.Ass):     return self.visit_ass(node, d)
        elif isinstance(node, ast.In):      return self.visit_in(node, d)
        elif isinstance(node, ast.Out):     return self.visit_out(node, d)
        elif isinstance(node, ast.If):      return self.visit_if(node, d)
        elif isinstance(node, ast.While):   return self.visit_while(node, d)
        elif isinstance(node, ast.For):     return self.visit_for(node, d)
        elif isinstance(node, ast.On):      return self.visit_on(node, d)
        elif isinstance(node, ast.Connect): return self.visit_connect(node, d)
        elif isinstance(node, ast.Aliases): return self.visit_aliases(node, d)
        elif isinstance(node, ast.Return):  return self.visit_return(node, d)
        else:
            raise Exception('Invalid statement')

    def visit_seq(self, node, d):
        self.buf.write((' '*d)+'{')
        self.buf.write(';\n'.join([self.stmt(x, d) for x in node.children()]))
        self.buf.write((' '*d)+'}')

    def visit_par(self, node, d):
        self.buf.write((' '*d)+'{')
        self.buf.write('|\n'.join([self.stmt(x, d) for x in node.children()]))
        self.buf.write((' '*d)+'}')

    def visit_skip(self, node, d):
        self.buf.write('skip')

    def visit_pcall(self, node, d):
        self.buf.write('pcall')

    def visit_ass(self, node, d):
        self.buf.write('ass')

    def visit_in(self, node, d):
        self.buf.write('in')

    def visit_out(self, node, d):
        self.buf.write('out')

    def visit_if(self, node, d):
        self.buf.write('if')

    def visit_while(self, node, d):
        self.buf.write('while')

    def visit_for(self, node, d):
        self.buf.write('for')

    def visit_on(self, node, d):
        self.buf.write('on')

    def visit_connect(self, node, d):
        self.buf.write('connect')

    def visit_aliases(self, node, d):
        self.buf.write('aliases')

    def visit_return(self, node, d):
        self.buf.write('return')

    # Expressions =========================================

    def exprlist(self, node):
        return ', '.join([x for x in node.children()])
    
    def expr(self, node):
        if   isinstance(node, ast.Unary): return self.visit_unary(node)
        elif isinstance(node, ast.Binop): return self.visit_binop(node)
        else: raise Exception('Invalid expression')

    def visit_unary(self, node):
        return '%s%s' % (node.op, self.elem(node.elem))

    def visit_binop(self, node):
        return '%s %s %s' % (self.elem(node.elem), 
                node.op, self.expr(node.right))
    
    # Elements= ===========================================

    def elem(self, node):
        if   isinstance(node, ast.Group):   return self.visit_group(node)
        elif isinstance(node, ast.Sub):     return self.visit_sub(node)
        elif isinstance(node, ast.Fcall):   return self.visit_fcall(node)
        elif isinstance(node, ast.Number):  return self.visit_number(node)
        elif isinstance(node, ast.Boolean): return self.visit_boolean(node)
        elif isinstance(node, ast.String):  return self.visit_string(node)
        elif isinstance(node, ast.Char):    return self.visit_char(node)
        elif isinstance(node, ast.Id):      return self.visit_id(node)
        else: raise Exception('Invalid element.')

    def visit_group(self, node):
        return '(%s)' % self.expr(node.expr)

    def visit_sub(self, node):
        return '%s[%s]' % (self.elem(node.name), self.expr(node.expr))

    def visit_fcall(self, node):
        return '%s(%s)' % (self.elem(node.name), self.exprlist(node.args))

    def visit_number(self, node):
        return node.value

    def visit_boolean(self, node):
        return node.value

    def visit_string(self, node):
        return node.value

    def visit_char(self, node):
        return node.value

    def visit_id(self, node):
        return node.value

