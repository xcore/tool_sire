import sys
import ast
from walker import NodeWalker

INDENT = 2
SEQ_INDENT = ';' + ' '*(INDENT-1)
PAR_INDENT = '|' + ' '*(INDENT-1) 

class Translate(NodeWalker):
    """ A walker class to pretty-print the AST in the langauge syntax 
    """
    def __init__(self, buf):
        super(Translate, self).__init__()
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
        self.decls(node.decls, 0)
        self.buf.write('\n')
        self.defs(node.defs, 0)
    
    # Variable declarations ===============================

    def decls(self, node, d):
        self.buf.write((self.indt(d) if len(node.children())>0 else '') 
                +(';\n'+self.indt(d)).join(
                    [self.decl(x) for x in node.children()]))
        if len(node.children())>0: self.buf.write(';\n')

    def decl_single(self, node):
        return '{} {}'.format(node.type, node.name)
    
    def decl_array(self, node):
        return '{} {}[{}]'.format(node.type, self.elem(node.name), 
                    self.expr(node.expr) if node.expr else '')
    
    def decl_val(self, node):
        return '{} := {}'.format(node.type.decl_str(node.name), 
                    self.expr(node.expr))
    
    def decl_port(self, node):
        return 'port {} : {}'.format(node.name, 
                    self.expr(node.expr))

    # Procedure declarations ==============================

    def defs(self, node, d):
        for p in node.children():
            self.defn(p, d)

    def def_proc(self, node, d):
        self.buf.write('proc {}({}) is\n'.format(
                node.name, self.formals(node.formals)))
        self.decls(node.decls, d+1)
        self.stmt(node.stmt, d+1)
        self.buf.write('\n\n')
    
    def def_func(self, node, d):
        self.buf.write('proc {}({}) is\n'.format(
                node.name, self.formals(node.formals)))
        self.decls(node.decls, d+1)
        self.stmt(node.stmt, d+1)
        self.buf.write('\n\n')
    
    # Formals =============================================
    
    def formals(self, node):
        return ', '.join([self.param(x) for x in node.children()])

    def param_var(self, node):
        return '{}'.format(node.name)

    def param_alias(self, node):
        return '{}[]'.format(node.name)

    def param_val(self, node):
        return 'val {}'.format(node.name)
    
    def param_chanend(self, node):
        return 'chanend {}'.format(node.name)

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
            node.name, self.expr_list(node.args)))

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

    def expr_list(self, node):
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
        return '{}[{}]'.format(node.name, self.expr(node.expr))

    def elem_fcall(self, node):
        return '{}({})'.format(node.name, self.exprlist(node.args))

    def elem_number(self, node):
        return '{}'.format(node.value)

    def elem_boolean(self, node):
        return '{}'.format(node.value)

    def elem_string(self, node):
        return '{}'.format(node.value)

    def elem_char(self, node):
        return '{}'.format(node.value)

    def elem_id(self, node):
        return node.name

