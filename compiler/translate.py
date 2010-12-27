import sys
import ast
from walker import NodeWalker

INDENT = 2
SEQ_INDENT = ';' + ' '*(INDENT-1)
PAR_INDENT = '|' + ' '*(INDENT-1) 

class Translate(NodeWalker):
    """ A walker class to translate the AST into XC
    """
    def __init__(self, buf=sys.stdout):
        self.buf = buf
        self.indent = [' '*INDENT]

    def out(self, d, s):
        """ Write an indented line """
        self.buf.write(self.indt(d)+s)

    def indt(self, d):
        """ Produce an indent """
        return (' '*INDENT)*(d-1) + (self.indent[-1] if d>0 else '')
    
    # Program ============================================

    def walk_program(self, node):
        self.vardecls(node.vardecls, 0)
        self.buf.write('\n')
        self.procdecls(node.procdecls, 0)
    
    # Variable declarations ===============================

    def vardecls(self, node, d):
        self.buf.write((self.indt(d) if len(node.children())>0 else '') 
                +(';\n'+self.indt(d)).join(
                    [self.vardecl(x) for x in node.children()]))
        if len(node.children())>0: self.buf.write(';\n')

    def vardecl(self, node):
        if node.form == "var":
            return '%s %s' % (node.type, self.elem(node.name))
        elif node.form == "array":
            return '{} {}[{}]'.format(node.type, self.elem(node.name), 
                    self.expr(node.expr) if node.expr else '')
        elif node.form == "val":
            return 'val {} := {}'.format(self.elem(node.name), 
                    self.expr(node.expr))
        elif node.form == "port":
            return 'port {} : {}'.format(self.elem(node.name), 
                    self.expr(node.expr))
        else:
            raise Exception('Invalid variable declaration')

    # Procedure declarations ==============================

    def procdecls(self, node, d):
        for p in node.children():
            self.procdecl(p, d)

    def procdecl(self, node, d):
        self.buf.write('{} {}({}) is\n'.format(
                node.type, self.elem(node.name), self.formals(node.formals)))
        self.vardecls(node.vardecls, d+1)
        self.stmt(node.stmt, d+1)
        self.buf.write('\n\n')
    
    # Formals =============================================
    
    def formals(self, node):
        return ', '.join([self.param(x) for x in node.children()])

    def param(self, node):
        if   node.type == "var":     return '{}'.format(self.elem(node.name))
        elif node.type == "alias":   return '{}[]'.format(self.elem(node.name))
        elif node.type == "val":     return 'val {}'.format(self.elem(node.name))
        elif node.type == "chanend": return 'chanend {}'.format(self.elem(node.name))
        else:
            raise Exception('Invalid parameter {}'.format(node))

    # Statements ==========================================

    def v_seq(self, node, d):
        self.buf.write(self.indt(d-1)+'{\n')
        self.indent.append(SEQ_INDENT)
        for x in node.children(): 
            self.stmt(x, d)
            self.buf.write('\n')
        self.indent.pop()
        self.buf.write(self.indt(d-1)+'}')

    def v_par(self, node, d):
        self.buf.write(self.indt(d-1)+'{\n')
        self.indent.append(PAR_INDENT)
        for x in node.children():
            self.stmt(x, d)
            self.buf.write('\n')
        self.indent.pop()
        self.buf.write(self.indt(d-1)+'}')

    def v_skip(self, node, d):
        self.out(d, 'skip')

    def v_pcall(self, node, d):
        self.out(d, '{}({})'.format(
            self.elem(node.name), self.v_exprlist(node.args)))

    def v_ass(self, node, d):
        self.out(d, '{} := {}'.format(
            self.elem(node.left), self.expr(node.expr)))

    def v_in(self, node, d):
        self.out(d, '{} ? {}'.format(
            self.elem(node.left), self.expr(node.expr)))

    def v_out(self, node, d):
        self.out(d, '{} ! {}'.format(
            self.elem(node.left), self.expr(node.expr)))

    def v_if(self, node, d):
        self.out(d, 'if {}\n'.format(self.expr(node.cond)))
        self.out(d, 'then\n')
        self.indent.append(' '*INDENT)
        self.stmt(node.thenstmt, d+1)
        self.buf.write('\n'+(self.indt(d))+'else\n')
        self.stmt(node.elsestmt, d+1)
        self.indent.pop()

    def v_while(self, node, d):
        self.out(d, 'while {} do\n'.format(self.expr(node.cond)))
        self.indent.append(' '*INDENT)
        self.stmt(node.stmt, d+1)
        self.indent.pop()

    def v_for(self, node, d):
        self.out(d, 'for {} to {} do\n'.format(self.elem(node.var),
            self.expr(node.init), self.expr(node.bound)))
        self.indent.append(' '*INDENT)
        self.stmt(node.stmt, d+1)
        self.indent.pop()

    def v_on(self, node, d):
        self.out(d, 'on {}: '.format(self.elem(node.core)))
        self.stmt(node.pcall, d)

    def v_connect(self, node, d):
        self.out(d, 'connect {} to {} : {}'.format(
            self.elem(node.left), self.elem(node.core), self.elem(node.dest)))

    def v_aliases(self, node, d):
        self.out(d, '{} aliases {}[{}..]'.format(
            self.elem(node.left), self.elem(node.name), 
            self.expr(node.expr)))

    def v_return(self, node, d):
        self.out(d, 'return {}'.format(self.expr(node.expr)))

    # Expressions =========================================

    def v_exprlist(self, node):
        return ', '.join([self.expr(x) for x in node.children()])
    
    def v_single(self, node):
        return self.elem(node.elem)

    def v_unary(self, node):
        return '({}{})'.format(node.op, self.elem(node.elem))

    def v_binop(self, node):
        return '{} {} {}'.format(self.elem(node.elem), 
                node.op, self.expr(node.right))
    
    # Elements= ===========================================

    def v_group(self, node):
        return '({})'.format(self.expr(node.expr))

    def v_sub(self, node):
        return '{}[{}]'.format(self.elem(node.name), self.expr(node.expr))

    def v_fcall(self, node):
        return '{}({})'.format(self.elem(node.name), self.v_exprlist(node.args))

    def v_number(self, node):
        return '{}'.format(node.value)

    def v_boolean(self, node):
        return '{}'.format(node.value)

    def v_string(self, node):
        return '{}'.format(node.value)

    def v_char(self, node):
        return '{}'.format(node.value)

    def v_id(self, node):
        return node.value

