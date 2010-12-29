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
            return 'int %s'.format(self.elem(node.name))
        elif node.form == "array":
            return 'int {}[{}]'.format(self.elem(node.name), 
                    self.expr(node.expr) if node.expr else '')
        elif node.form == "val":
            return '#define {} {}'.format(self.elem(node.name), 
                    self.expr(node.expr))
        elif node.form == "port":
            return '#define {} {}'.format(self.elem(node.name), 
                    self.expr(node.expr))
        else:
            raise Exception('Invalid variable declaration')

    # Procedure declarations ==============================

    def procdecls(self, node, d):
        for p in node.children():
            self.procdecl(p, d)

    def procdecl(self, node, d):
        self.buf.write('unsigned {}({}) is\n'.format(
                node.type, self.elem(node.name), self.formals(node.formals)))
        self.vardecls(node.vardecls, d+1)
        self.stmt(node.stmt, d+1)
        self.buf.write('\n\n')
    
    # Formals =============================================
    
    def formals(self, node):
        return ', '.join([self.param(x) for x in node.children()])

    def param(self, node):
        if   node.type == "var":     return 'int &{}'.format(self.elem(node.name))
        elif node.type == "alias":   return 'int {}[]'.format(self.elem(node.name))
        elif node.type == "val":     return 'int {}'.format(self.elem(node.name))
        elif node.type == "chanend": return 'unsigned {}'.format(self.elem(node.name))
        else:
            raise Exception('Invalid parameter {}'.format(node))

    # Statements ==========================================

    def stmt_seq(self, node, d):
        self.buf.write(self.indt(d-1)+'{\n')
        self.indent.append(SEQ_INDENT)
        for x in node.children(): 
            self.stmt(x, d)
            self.buf.write('\n')
        self.indent.pop()
        self.buf.write(self.indt(d-1)+'}')

    def stmt_par(self, node, d):
        self.buf.write(self.indt(d-1)+'{\n')
        self.indent.append(PAR_INDENT)
        for x in node.children():
            self.stmt(x, d)
            self.buf.write('\n')
        self.indent.pop()
        self.buf.write(self.indt(d-1)+'}')

    def stmt_skip(self, node, d):
        self.out(d, 'skip')

    def stmt_pcall(self, node, d):
        self.out(d, '{}({})'.format(
            self.elem(node.name), self.exprlist(node.args)))

    def stmt_ass(self, node, d):
        self.out(d, '{} := {}'.format(
            self.elem(node.left), self.expr(node.expr)))

    def stmt_in(self, node, d):
        self.out(d, '{} ? {}'.format(
            self.elem(node.left), self.expr(node.expr)))

    def stmt_out(self, node, d):
        self.out(d, '{} ! {}'.format(
            self.elem(node.left), self.expr(node.expr)))

    def stmt_if(self, node, d):
        self.out(d, 'if {}\n'.format(self.expr(node.cond)))
        self.out(d, 'then\n')
        self.indent.append(' '*INDENT)
        self.stmt(node.thenstmt, d+1)
        self.buf.write('\n'+(self.indt(d))+'else\n')
        self.stmt(node.elsestmt, d+1)
        self.indent.pop()

    def stmt_while(self, node, d):
        self.out(d, 'while {} do\n'.format(self.expr(node.cond)))
        self.indent.append(' '*INDENT)
        self.stmt(node.stmt, d+1)
        self.indent.pop()

    def stmt_for(self, node, d):
        self.out(d, 'for {} to {} do\n'.format(self.elem(node.var),
            self.expr(node.init), self.expr(node.bound)))
        self.indent.append(' '*INDENT)
        self.stmt(node.stmt, d+1)
        self.indent.pop()

    def stmt_on(self, node, d):
        self.out(d, 'on {}: '.format(self.elem(node.core)))
        self.stmt(node.pcall, d)

    def stmt_connect(self, node, d):
        self.out(d, 'connect {} to {} : {}'.format(
            self.elem(node.left), self.elem(node.core), self.elem(node.dest)))

    def stmt_aliases(self, node, d):
        self.out(d, '{} aliases {}[{}..]'.format(
            self.elem(node.left), self.elem(node.name), 
            self.expr(node.expr)))

    def stmt_return(self, node, d):
        self.out(d, 'return {}'.format(self.expr(node.expr)))

    # Expressions =========================================

    def exprlist(self, node):
        return ', '.join([self.expr(x) for x in node.children()])
    
    def expr_single(self, node):
        return self.elem(node.elem)

    def expr_unary(self, node):
        return '({}{})'.format(node.op, self.elem(node.elem))

    def expr_binop(self, node):
        return '{} {} {}'.format(self.elem(node.elem), 
                node.op, self.expr(node.right))
    
    # Elements= ===========================================

    def elem_group(self, node):
        return '({})'.format(self.expr(node.expr))

    def elem_sub(self, node):
        return '{}[{}]'.format(self.elem(node.name), self.expr(node.expr))

    def elem_fcall(self, node):
        return '{}({})'.format(self.elem(node.name), self.exprlist(node.args))

    def elem_number(self, node):
        return '{}'.format(node.value)

    def elem_boolean(self, node):
        return '{}'.format(node.value)

    def elem_string(self, node):
        return '{}'.format(node.value)

    def elem_char(self, node):
        return '{}'.format(node.value)

    def elem_id(self, node):
        return node.value

