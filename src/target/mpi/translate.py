# Copyright (c) 2011, James Hanlon, All rights reserved
# This software is freely distributable under a derivative of the
# University of Illinois/NCSA Open Source License posted in
# LICENSE.txt and at <http://github.xcore.com/>

import sys

import definitions as defs
import config as config
import ast
from walker import NodeWalker
from type import Type
from blocker import Blocker
from blocker import INDENT

op_conversion = {
    '+'   : '+',
    '-'   : '-',
    '*'   : '*',
    '/'   : '/',
    'rem' : '%',
    'or'  : '||',
    'and' : '&&',
    'xor' : '^',
    '&'   : '&',
    'lor' : '|',
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
    'printstrln' : 'printf',
}

class TranslateMPI(NodeWalker):
    """ A walker class to pretty-print the AST in the langauge syntax 
    """
    def __init__(self, semantics, children, buf):
        super(TranslateMPI, self).__init__()
        self.sem = semantics
        self.child = children
        self.buf = buf
        self.indent = [INDENT]
        self.blocker = Blocker(self, buf)
        self.label_counter = 0
        self.parent = None

    def out(self, s):
        """ Write an indented line
        """
        self.blocker.insert(s)

    def asm(self, template, outop=None, inops=None, clobber=None):
        """ Write an inline assembly statement
        """
        self.out('asm("{}"{}{}{}{}{}{});'.format(
            #template.replace('\n', ' ; '),
            template,
            ':' if outop or inops or clobber else '',
            '"=r"('+outop+')' if outop else '', 
            ':' if inops or clobber  else '', 
            ', '.join(['"r"('+x+')' for x in inops]) if inops else '',
            ':'   if clobber else '',
            ', '.join(['"'+x+'"' for x in clobber]) if clobber else ''
            ))

    def comment(self, s):
        """ Write a comment
        """
        self.out('// '+s)

    def stmt_block(self, stmt):
        """ Decide whether the statement needs a block
        """
        if not (isinstance(stmt, ast.StmtSeq) 
                or isinstance(stmt, ast.StmtPar)):
            self.blocker.begin()
            self.stmt(stmt)
            self.blocker.end()
        else:
            self.stmt(stmt)
        
    def procedure_name(self, name):
        """ If a procedure name has a conversion, return it
        """
        return proc_conversion[name] if name in proc_conversion else name

    def arguments(self, arg_list):
        """ Build the list of arguments. If there is an array reference 
            proper, it must be loaded manually.
        """
        args = []
        for x in arg_list.children():
            # For single array arguments, load the address given by this
            # variable manually to circumvent an XC type error.
            arg = None
            if isinstance(x, ast.ExprSingle):
                if isinstance(x.elem, ast.ElemId):
                    if x.elem.symbol.type.form == 'array':
                        tmp = self.blocker.get_tmp()
                        self.asm('mov %0, %1', outop=tmp,
                                inops=[x.elem.name])
                        arg = tmp
            args.append(arg if arg else self.expr(x))
        return ', '.join(args)

    def get_label(self):
        """ Get the next unique label
        """
        l = '_L{}'.format(self.label_counter)
        self.label_counter += 1
        return l

    def header(self):
        self.out('#include <mpi.h>')
        self.out('#include <stdlib.h>')
        self.out('#include <stdio.h>')
        self.out('#include <syscall.h>')
        #self.out('#include "globals.h"')
        #self.out('#include "util.h"')
        #self.out('#include "guest.h"')
        self.out('#include "program.h"')
        self.out('#include "device.h"')
        self.out('#include "language.h"')
        self.out('')
 
    def create_main(self):
        self.out(MAIN_FUNCTION)

    # Program ============================================

    def walk_program(self, node):

        # Walk the entire program
        self.header()
        self.decls(node.decls)
        self.defs(node.defs, 0)
   
        # Output the buffered blocks
        self.blocker.output()
    
    # Variable declarations ===============================

    def decls(self, node):
        for x in node.children():
            self.out(self.decl(x))
        if len(node.children()) > 0:
            self.out('')

    def decl(self, node):
        s = '{}'.format(node.name)

        # Forms
        if node.type.form == 'array':
            s += '[{}]'.format(self.expr(node.expr))
        elif node.type.form == 'alias':
            return 'unsigned '+s+';'
        
        # Specifiers
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
        s = ''
        s += 'void' if node.name == '_main' else 'int'
        s += ' {}({})'.format(
                self.procedure_name(node.name),
                self.formals(node.formals))
        self.parent = node.name
        self.out(s)
        self.blocker.begin()
        self.decls(node.decls)
        self.stmt_block(node.stmt)
        self.blocker.end()
        self.out('')
    
    # Formals =============================================
    
    def formals(self, node):
        return ', '.join([self.param(x) for x in node.children()])

    def param(self, node):
        s = '{}'.format(node.name)

        # Forms
        if node.type.form == 'alias':
            return 'unsigned '+s

        # Specifiers
        if node.type == Type('var', 'single'):
            s = '&' + s
        if (node.type.specifier == 'var' 
                or node.type.specifier == 'val'):
            s = 'int ' + s
        if node.type.specifier == 'chanend':
            s = 'unsigned '+s

        return s

    # Statements ==========================================

    def stmt_seq(self, node):
        self.blocker.begin()
        for x in node.children(): 
            self.stmt(x)
        self.blocker.end()

    def stmt_par(self, node):
        """ Generate a parallel block
        """
        self.blocker.begin()
        self.comment('Parallel block')

        for (i, x) in enumerate(node.children()):
            self.comment('Thread {}'.format(i))
            self.stmt(x)

        self.blocker.end()

    def stmt_skip(self, node):
        pass

    def stmt_pcall(self, node):
        self.out('{}({});'.format(
            self.procedure_name(node.name), self.arguments(node.args)))

    def stmt_ass(self, node):
    
        # If the target is an alias, then generate a store after
        if node.left.symbol.type.form == 'alias':
            tmp = self.blocker.get_tmp()
            self.out('{} = {};'.format(tmp, self.expr(node.expr)))
            self.asm('stw %0, %1[%2]', 
                    inops=[tmp, node.left.name, self.expr(node.left.expr)])
        
        # Otherwise, proceede normally
        else:
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
        self.out('for ({0} = {1}; {0} <= {2}; {0} += {3})'.format(
            self.elem(node.var), self.expr(node.init), 
            self.expr(node.bound), self.expr(node.step)))
        self.stmt_block(node.stmt)

    def stmt_on(self, node):
        """ Generate an on statement 
        """
        proc_name = node.pcall.name
        num_args = len(node.pcall.args.expr) if node.pcall.args.expr else 0 
        num_procs = len(self.child.children[proc_name]) + 1
        
        # Calculate closure size 
        closure_size = 2 + num_procs;
        for (i, x) in enumerate(node.pcall.args.expr):
            t = self.sem.sig.lookup_param_type(proc_name, i)
            if t.form == 'alias': closure_size = closure_size + 3
            elif t.form == 'single': closure_size = closure_size + 2 

        self.comment('On')
        
        self.blocker.begin()
        self.out('unsigned _closure[{}];'.format(closure_size))
        n = 0

        # Header: (#args, #procs)
        self.comment('Header: (#args, #procs)')
        self.out('_closure[{}] = {};'.format(n, num_args)) ; n+=1
        self.out('_closure[{}] = {};'.format(n, num_procs)) ; n+=1

        # Arguments: 
        #   Array: (0, length, address)
        #   Var:   (1, address)
        #   Val:   (2, value)
        if node.pcall.args.expr:
            for (i, x) in enumerate(node.pcall.args.expr):
                t = self.sem.sig.lookup_param_type(proc_name, i)

                # If the parameter type is an array reference
                if t.form == 'alias':

                    # Output the length of the array
                    q = self.sem.sig.lookup_array_qualifier(proc_name, i)
                    self.comment('alias')
                    self.out('_closure[{}] = t_arg_ALIAS;'.format(n)) ; n+=1
                    self.out('_closure[{}] = {};'.format(n,
                        self.expr(node.pcall.args.expr[q]))) ; n+=1
                   
                    # If the elem is a proper array, load the address
                    if x.elem.symbol.type.form == 'array':
                        tmp = self.blocker.get_tmp()
                        self.asm('mov %0, %1', outop=tmp, inops=[x.elem.name])
                        self.out('_closure[{}] = {};'.format(n, tmp)) ; n+=1
                    # Otherwise, just assign
                    if x.elem.symbol.type.form == 'alias':
                        self.out('_closure[{}] = {};'.format(n, self.expr(x))) ; n+=1
                
                # Otherwise, a var or val single
                elif t.form == 'single':

                    if t.specifier == 'var':
                        self.comment('var')
                        self.out('_closure[{}] = t_arg_VAR;'.format(n)) ; n+=1
                        tmp = self.blocker.get_tmp()
                        self.asm('mov %0, %1', outop=tmp,
                                inops=['('+x.elem.name+', unsigned[])'])
                        self.out('_closure[{}] = {};'.format(n, tmp)) ; n+=1
                    elif t.specifier == 'val':
                        self.comment('val')
                        self.out('_closure[{}] = t_arg_VAL;'.format(n)) ; n+=1
                        self.out('_closure[{}] = {};'.format(n, self.expr(x))) ; n+=1

        # Procedures: (jumpindex)*
        self.comment('Proc: parent '+proc_name)
        self.out('_closure[{}] = {};'.format(n, defs.JUMP_INDEX_OFFSET
                +self.sem.proc_names.index(proc_name))) ; n+=1
        for x in self.child.children[proc_name]:
            self.comment('Proc: child '+x)
            self.out('_closure[{}] = {};'.format(n, defs.JUMP_INDEX_OFFSET
                    +self.sem.proc_names.index(x))) ; n+=1

        # Call runtime TODO: length argument?
        self.out('{}({}, _closure);'.format(defs.LABEL_MIGRATE, 
            self.expr(node.core.expr)))

        self.blocker.end()

    def stmt_connect(self, node):
        self.out('connect {} to {} : {};'.format(
            self.elem(node.left), self.elem(node.core), self.elem(node.dest)))

    def stmt_aliases(self, node):
        self.asm('add %0, %1, %2', outop=node.dest, 
                inops=[node.name, '({})*{}'.format(
                    self.elem(node.expr), defs.BYTES_PER_WORD)])

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
        return '{}[{}]'.format(node.name, self.expr(node.expr))

    def elem_fcall(self, node):
        return '{}({})'.format(node.name, self.arguments(node.args))

    def elem_number(self, node):
        return '{}'.format(node.value)

    def elem_boolean(self, node):
        return '{}'.format(node.value.upper())

    def elem_string(self, node):
        return '{}'.format(node.value)

    def elem_char(self, node):
        return '{}'.format(node.value)

    def elem_id(self, node):
        return node.name
