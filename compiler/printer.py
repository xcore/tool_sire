# Copyright (c) 2011, James Hanlon, All rights reserved
# This software is freely distributable under a derivative of the
# University of Illinois/NCSA Open Source License posted in
# LICENSE.txt and at <http://github.xcore.com/>

import sys

import ast
from walker import NodeWalker
from type import Type

INDENT = 2
FIRST_INDENT = '^'
SEQ_INDENT = ';' + ' '*(INDENT-1)
PAR_INDENT = '|' + ' '*(INDENT-1) 

class Printer(NodeWalker):
    """ 
    A walker class to pretty-print the AST in the langauge syntax.
    """
    def __init__(self, buf=sys.stdout):
        super(Printer, self).__init__()
        self.buf = buf
        self.indent = [' '*INDENT]

    def out(self, d, s):
        """ 
        Write an indented line.
        """
        self.buf.write(self.indt(d)+s)

    def indt(self, d):
        """ 
        Produce an indent. If its the first statement of a seq or par block we
        only produce a single space.
        """
        return (' ' if self.indent[-1]==FIRST_INDENT else 
            (' '*INDENT)*(d-1) + (self.indent[-1] if d>0 else ''))
    
    def arg_list(self, args):
        return ', '.join([self.expr(x) for x in args])

    def var_decls(self, decls, d):
        # Procedure declarations
        self.buf.write((self.indt(d) if len(decls)>0 else '')
                +(';\n'+self.indt(d)).join(
                [self.decl(x) for x in decls]))
        if len(decls)>0: self.buf.write(';\n')

    
    # Program ============================================

    def walk_program(self, node):
        
        # Program declarations
        self.var_decls(node.decls, 0)

        self.buf.write('\n')
       
        # Program definitions (procedures)
        [self.defn(x, 0) for x in node.defs]
    
    # Variable declarations ===============================

    def decl(self, node):
        s = '{}'.format(node.name)
        if node.type == Type('var', 'array'):
            s += '[{}]'.format(self.expr(node.expr))
        elif node.type == Type('ref', 'array'):
            s += '[]'
        if node.type.specifier == 'val':
            s = 'val {} := {}'.format(s, self.expr(node.expr))
        else:
            s = '{} {}'.format(node.type.specifier, s)
        return s

    # Procedure declarations ==============================

    def defn(self, node, d):
        
        # Procedure definition
        name = node.name if node.name != '_main' else 'main'
        self.buf.write('{} {}({}) is\n'.format(node.type.specifier, name, 
                ', '.join([self.param(x) for x in node.formals])))
        
        # Procedure declarations
        self.var_decls(node.decls, d+1)

        # Statement block
        self.stmt(node.stmt, d+1)
        self.buf.write('\n\n')
    
    # Formals =============================================
    
    def param(self, node):
        if node.type == Type('val', 'single'):
            return 'val '+node.name
        elif node.type == Type('ref', 'single'):
            return 'var '+node.name
        elif node.type == Type('val', 'array'):
            return 'var {}[{}]'.format(node.name, self.expr(node.expr))
        elif node.type == Type('ref', 'array'):
            return 'var {}[{}]'.format(node.name, self.expr(node.expr))
        else:
            assert 0

    # Statements ==========================================

    def stmt_seq(self, node, d):
        self.buf.write(self.indt(d-1)+'{')
        self.indent.append(FIRST_INDENT)
        for (i, x) in enumerate(node.children()): 
            self.stmt(x, d+1)
            self.buf.write('\n')
            if i==0:
                self.indent.pop()
                self.indent.append(SEQ_INDENT)
        self.indent.pop()
        self.buf.write(self.indt(d-1)+'}')

    def stmt_par(self, node, d):
        self.buf.write(self.indt(d-1)+'{')
        self.indent.append(FIRST_INDENT)
        for (i, x) in enumerate(node.children()):
            self.stmt(x, d+1)
            self.buf.write('\n')
            if i==0:
                self.indent.pop()
                self.indent.append(PAR_INDENT)
        self.indent.pop()
        self.buf.write(self.indt(d-1)+'}')

    def stmt_skip(self, node, d):
        self.out(d, 'skip')

    def stmt_pcall(self, node, d):
        self.out(d, '{}({})'.format(
            node.name, self.arg_list(node.args)))

    def stmt_ass(self, node, d):
        self.out(d, '{} := {}'.format(
            self.elem(node.left), self.expr(node.expr)))

    def stmt_alias(self, node, d):
        self.out(d, '{} aliases {}'.format(
            node.name, self.expr(node.slice)))

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
        self.out(d, 'for {} := {} to {} step {} do\n'.format(
            self.elem(node.var), self.expr(node.init), 
            self.expr(node.step), self.expr(node.bound)))
        self.indent.append(' '*INDENT)
        self.stmt(node.stmt, d+1)
        self.indent.pop()

    def stmt_rep(self, node, d):
        self.out(d, 'par {} := {} for {} do\n'.format(
            self.elem(node.var), self.expr(node.init), 
            self.expr(node.count)))
        self.indent.append(' '*INDENT)
        self.stmt(node.stmt, d+1)
        self.indent.pop()

    def stmt_on(self, node, d):
        self.out(d, 'on {} do {}'.format(self.elem(node.core), 
            self.elem(node.pcall)))

    def stmt_return(self, node, d):
        self.out(d, 'return {}'.format(self.expr(node.expr)))

    # Expressions =========================================

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

    def elem_slice(self, node):
        return '{}[{} : {}]'.format(node.name, 
                self.expr(node.begin), self.expr(node.end))

    def elem_fcall(self, node):
        return '{}({})'.format(node.name, self.arg_list(node.args))

    def elem_pcall(self, node):
        return '{}({})'.format(node.name, self.arg_list(node.args))

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

