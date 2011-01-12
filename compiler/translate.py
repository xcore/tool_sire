import sys
import ast
import printer
from walker import NodeWalker
from type import Type

INDENT = '  '
SCRATCH_VAR = '_x_'

op_conversion = {
    '+'   : '+',
    '-'   : '-',
    '*'   : '*',
    '/'   : '/',
    'rem' : '%',
    'or'  : '||',
    'and' : '&&',
    'xor' : '^',
    '~'   : '!',
    '<<'  : '<<',
    '>>'  : '>>',
    '<'   : '<',
    '>'   : '>',
    '<='  : '<=',
    '>='  : '>=',
    '='   : '==',
    '~='  : '!=',
}

proc_conversion = {
    'printval' : 'printint',
    'printstr' : 'printstr',
}

class Blocker(object):
    """ A class to buffer and output blocks containing statements
    """
    def __init__(self, translator, buf):
        self.translator = translator
        self.buf = buf
        self.stack = []

    def begin(self):
        self.stack.append('^')

    def end(self):
        self.stack.append('*')

    def insert(self, s):
        self.stack.append(s)
    
    def insert_before(self, s):
        self.stack.insert(len(self.stack), s)

    def output(self):
        depth = 0
        for x in self.stack:
            if x == '$':
                depth += 1
            elif x == '%':
                depth -= 1
            elif x == '^':
                self.out(depth, '{\n')
                depth += 1
            elif x == '*':
                depth -= 1
                self.out(depth, '}\n')
            else:
                self.out(depth, x+'\n')

    def out(self, d, s):
        """ Write an indented line """
        self.buf.write((INDENT*d)+s)


class Translate(NodeWalker):
    """ A walker class to pretty-print the AST in the langauge syntax 
    """
    
    def __init__(self, semantics, buf):
        super(Translate, self).__init__()
        self.sem = semantics
        self.buf = buf
        self.indent = [INDENT]
        self.blocker = Blocker(self, buf)
        self.printer = printer.Printer(buf)

    def out(self, s):
        """ Write an indented line """
        self.blocker.insert(s)

    def asm(self, template, outops=None, inops=None, clobber=None):
        """ Write an inline assembly statement """
        self.out('asm("{}"{}{}{}{}{}{});'.format(
            template,
            ' : '   if outops or inops or clobber else '',
            outops  if outops  else '', 
            ' : '   if inops or clobber  else '', 
            inops   if inops else '',
            ' : '   if clobber else '',
            clobber if clobber else ''
            ))

    def ppt(self, method, node):
        """ Display a pretty-printed AST node in a comment """
        self.out('/*\n')
        #getattr(self.printer, method)(node, 0)
        self.out('\n')
        self.out('*/\n')

    def stmt_block(self, stmt):
        """ Decide whether the statement needs a block """
        if not (isinstance(stmt, ast.StmtSeq) 
                or isinstance(stmt, ast.StmtPar)):
            self.blocker.begin()
            self.stmt(stmt)
            self.blocker.end()
        else:
            self.stmt(stmt)

    def header(self):
        self.buf.write('#include <xs1.h>\n')
        self.buf.write('#include <platform.h>\n')
        self.buf.write('#include <print.h>\n')
    
    # Program ============================================

    def walk_program(self, node):
        self.header()
        self.out('')
        self.decls(node.decls)
        self.out('')
        self.defs(node.defs, 0)
        self.blocker.output()
    
    # Variable declarations ===============================

    def decls(self, node):
        #self.buf.write((INDENT*d if len(node.children())>0 else '') 
        #        +(';\n'+(INDENT*d)).join(
        #            [self.decl(x) for x in node.children()]))
        #if len(node.children())>0: self.buf.write(';\n')
        for x in node.children():
            self.out(self.decl(x))

    def decl(self, node):
        s = '{}'.format(node.name)
        if node.type.form == 'array':
            s += '[{}]'.format(self.expr(node.expr))
        elif node.type.form == 'alias':
            s += '[1]'
        if node.type.specifier == 'var':
            s = 'int {}'.format(s)+';'
        elif node.type.specifier == 'val':
            s = '#define {} {}'.format(s, self.expr(node.expr))
        elif node.type.specifier == 'port':
            s = 'const unsigned {} = {};'.format(s, self.expr(node.expr))
        else:
            s = '{} {}'.format(node.type.specifier, s)
        return s

    # Procedure declarations ==============================

    def defs(self, node, d):
        for p in node.children():
            self.defn(p, d)

    def defn(self, node, d):
        self.out('#pragma unsafe arrays')
        s = ''
        if node.type.specifier == 'proc':
            s += 'void'
        elif node.type.specifier == 'func':
            s += 'int'
        s += ' {}({})'.format(
                node.name, self.formals(node.formals))
        self.out(s)
        self.blocker.begin()
        self.decls(node.decls)
        # Add the scratch variable to the procedure scope
        self.out('unsigned ' + SCRATCH_VAR + ';')
        self.stmt_block(node.stmt)
        self.blocker.end()
        self.out('')
    
    # Formals =============================================
    
    def formals(self, node):
        return ', '.join([self.param(x) for x in node.children()])

    def param(self, node):
        s = '{}'.format(node.name)
        if node.type.form == 'alias':
            s += '[]'
        if node.type == Type('var', 'single'):
            s = '&' + s
        elif node.type.specifier == 'var' or node.type.specifier == 'val':
            s = 'int ' + s
        elif node.type.specifier == 'chanend':
            s = 'unsigned '+s
        return s

    # Statements ==========================================

    def stmt_seq(self, node):
        self.blocker.begin()
        for x in node.children(): 
            self.stmt(x)
        self.blocker.end()

    def stmt_par(self, node):
        #self.buf.write(self.indt(d-1)+'par {\n')
        #for x in node.children():
        #    self.stmt(x)
        #    self.buf.write('\n')
        #self.buf.write(self.indt(d-1)+'}')
        pass

    def stmt_skip(self, node):
        pass

    def stmt_pcall(self, node):
        name = node.name
        # Check for conversion (TODO: neaten this)
        if node.name in proc_conversion:
            name = proc_conversion[node.name] 
        self.out('{}({});'.format(
            name, self.expr_list(node.args)))

    def stmt_ass(self, node):
        self.out('{} = {};'.format(
            self.elem(node.left), self.expr(node.expr)))

    def stmt_in(self, node):
        self.out('{} ? {};'.format(
            self.elem(node.left), self.expr(node.expr)))

    def stmt_out(self, node):
        self.out('{} ! {};'.format(
            self.elem(node.left), self.expr(node.expr)))

    def stmt_if(self, node):
        self.out('if ({})'.format(self.expr(node.cond)))
        self.stmt_block(node.thenstmt)
        if not isinstance(node.elsestmt, ast.StmtSkip):
            self.out('else')
            self.stmt_block(node.elsestmt)

    def stmt_while(self, node):
        self.out('while ({})'.format(self.expr(node.cond)))
        self.stmt_block(node.stmt)
    
    def stmt_for(self, node):
        self.out('for ({0} = {1}; {0} < {2}; {0}++)'.format(
            self.elem(node.var),
            self.expr(node.init), self.expr(node.bound)))
        self.stmt_block(node.stmt)

    def stmt_on(self, node):
        self.out('on {}: '.format(self.elem(node.core)))
        self.stmt(node.pcall)
        self.out(';')

    def stmt_connect(self, node):
        self.out('connect {} to {} : {};'.format(
            self.elem(node.left), self.elem(node.core), self.elem(node.dest)))

    def stmt_aliases(self, node):
        self.asm('add %0, %1, %2', 
                outops='"=r"('+SCRATCH_VAR+')', 
                inops='"r"('+node.name+'), "r"('+self.elem(node.expr)+')')
        self.asm('stw %0, %1[0x0]', 
                inops='"r"('+SCRATCH_VAR+'), "r"('+node.dest+')')

    def stmt_return(self, node):
        self.out('return {};'.format(self.expr(node.expr)))

    # Expressions =========================================

    def expr_list(self, node):
        return ', '.join([self.expr(x) for x in node.children()])
    
    def expr_single(self, node):
        return self.elem(node.elem)

    def expr_unary(self, node):
        return '({}{})'.format(node.op, self.elem(node.elem))

    def expr_binop(self, node):
        return '{} {} {}'.format(self.elem(node.elem), 
                op_conversion[node.op], self.expr(node.right))
    
    # Elements= ===========================================

    def elem_group(self, node):
        return '({})'.format(self.expr(node.expr))

    def elem_sub(self, node):
        # If the index is a constant value, assign it to a variable first to
        # that the compiler will allow an unsafe access to the array
        if self.sem.get_expr_type(node.expr) == Type('val', 'single'):
            self.blocker.insert_before(SCRATCH_VAR+' = '+self.expr(node.expr));
            return '{}[{}]'.format(node.name, SCRATCH_VAR)
        else:
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

