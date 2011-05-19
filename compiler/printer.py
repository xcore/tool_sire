# Copyright (c) 2011, James Hanlon, All rights reserved
# This software is freely distributable under a derivative of the
# University of Illinois/NCSA Open Source License posted in
# LICENSE.txt and at <http://github.xcore.com/>

import sys

import ast
from walker import NodeWalker
from type import Type

INDENT       = '  '
BLOCK_INDENT = '{ '
SEQ_INDENT   = '; '
PAR_INDENT   = '| ' 

class Printer(NodeWalker):
    """ 
    A walker class to pretty-print the AST in the langauge syntax.
    """
    def __init__(self, buf=sys.stdout):
        super(Printer, self).__init__()
        self.buf = buf
        self.indent = []

    def indt(self):
        """ 
        Produce an indent. If its the first statement of a seq or par block we
        only produce a single space.
        """
        if len(self.indent) == 0:
            return '  '
        else:
            return '  '*(len(self.indent)-1)+self.indent[-1]
    
    def out(self, s):
        """ 
        Write an indented line.
        """
        self.buf.write(self.indt()+s)

    def arg_list(self, args):
        return ', '.join([self.expr(x) for x in args])

    def var_decls(self, decls):
        # Procedure declarations
        self.buf.write((self.indt() if len(decls)>0 else '')
                +(';\n'+self.indt()).join(
                [self.decl(x) for x in decls]))
        if len(decls)>0: self.buf.write(';\n')

    
    # Program ============================================

    def walk_program(self, node):
        
        # Program declarations
        self.indent.append(INDENT)
        self.var_decls(node.decls)
        self.buf.write('\n')
        self.indent.pop()
       
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
        self.indent.append(INDENT)
        self.var_decls(node.decls)

        # Statement block
        self.indent.pop()
        self.stmt(node.stmt)
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

    def stmt_block(self, node, indent):
        """
        Output a block of statements. E.g.:
          { stmt1
          ; stmt2
          ; { stmt3
            | stmt4
            }
          ; stmt5
          }
        """
        if len(self.indent)>0:
            self.indent.pop()
        self.indent.append(BLOCK_INDENT)
        for (i, x) in enumerate(node.stmt): 
            self.stmt(x) ; self.buf.write('\n')
            if i==0:
                self.indent.pop()
                self.indent.append(indent)
        self.indent.pop()
        self.out('}')

    def stmt_seq(self, node):
        self.stmt_block(node, SEQ_INDENT)

    def stmt_par(self, node):
        self.stmt_block(node, PAR_INDENT)

    def stmt_skip(self, node):
        self.out('skip')

    def stmt_pcall(self, node):
        self.out('{}({})'.format(
            node.name, self.arg_list(node.args)))

    def stmt_ass(self, node):
        self.out('{} := {}'.format(
            self.elem(node.left), self.expr(node.expr)))

    def stmt_alias(self, node):
        self.out('{} aliases {}'.format(
            node.name, self.expr(node.slice)))

    def stmt_if(self, node):
        self.out('if {}\n'.format(self.expr(node.cond)))
        self.out('then\n')
        self.indent.append(INDENT)
        self.stmt(node.thenstmt)
        self.buf.write('\n'+(self.indt())+'else\n')
        self.stmt(node.elsestmt)
        self.indent.pop()

    def stmt_while(self, node):
        self.out('while {} do\n'.format(self.expr(node.cond)))
        self.indent.append(INDENT)
        self.stmt(node.stmt)
        self.indent.pop()

    def stmt_for(self, node):
        self.out('for {} := {} to {} step {} do\n'.format(
            self.elem(node.var), self.expr(node.init), 
            self.expr(node.step), self.expr(node.bound)))
        self.indent.append(INDENT)
        self.stmt(node.stmt)
        self.indent.pop()

    def stmt_rep(self, node):
        self.out('par {} := {} for {} do\n'.format(
            self.elem(node.var), self.expr(node.init), 
            self.expr(node.count)))
        self.indent.append(INDENT)
        self.stmt(node.stmt)
        self.indent.pop()

    def stmt_on(self, node):
        self.out('on {} do {}'.format(self.elem(node.core), 
            self.elem(node.pcall)))

    def stmt_return(self, node):
        self.out('return {}'.format(self.expr(node.expr)))

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

