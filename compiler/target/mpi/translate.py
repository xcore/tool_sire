# Copyright (c) 2011, James Hanlon, All rights reserved
# This software is freely distributable under a derivative of the
# University of Illinois/NCSA Open Source License posted in
# LICENSE.txt and at <http://github.xcore.com/>

import sys

import definitions as defs
import config as config
import ast
from walker import NodeWalker
from typedefs import *
from blocker import Blocker
from blocker import INDENT

op_conversion = {
  '+'   : '+',
  '-'   : '-',
  '*'   : '*',
  '/'   : '/',
  'rem' : '%',
  'or'  : '|',
  'and' : '&',
  'xor' : '^',
  '~'   : '~',
  '<<'  : '<<',
  '>>'  : '>>',
  '<'   : '<',
  '>'   : '>',
  '<='  : '<=',
  '>='  : '>=',
  '='   : '==',
  '~='  : '!=',
  }

builtin_conversion = {
  # Printing
  'printchar'   : '_PRINTCHAR',
  'printcharln' : '_PRINTCHARLN',
  'printval'  : '_PRINTVAL',
  'printvalln'  : '_PRINTVALLN',
  'printhex'  : '_PRINTHEX',
  'printhexln'  : '_PRINTHEXLN',
  'printstr'  : '_PRINTSTR',
  'printstrln'  : '_PRINTSTRLN',
  'println'   : '_PRINTLN',
  # Fixed point
  'mulf8_24'  : 'mulf8_24',
  'divf8_24'  : 'divf8_24',
  # System
  'procid'    : 'procid'
  }

class TranslateMPI(NodeWalker):
  """ 
  A walker class to pretty-print the AST in the langauge syntax.
  """
  def __init__(self, sig, child, buf):
    super(TranslateMPI, self).__init__()
    self.sig = sig
    self.child = child
    self.buf = buf
    self.indent = [INDENT]
    self.blocker = Blocker(self, buf)
    self.parent = None

  def out(self, s):
    """ 
    Write an indented line.
    """
    self.blocker.insert(s)

  def comment(self, s):
    """ 
    Write a comment.
    """
    self.out('// '+s)

  def stmt_block(self, stmt):
    """ 
    Decide whether the statement needs a block.
    """
    if not (isinstance(stmt, ast.StmtSeq) 
        or isinstance(stmt, ast.StmtPar)):
      self.blocker.begin()
      self.stmt(stmt)
      self.blocker.end()
    else:
      self.stmt(stmt)
    
  def procedure_name(self, name):
    """ 
    If a procedure name has a conversion, return it.
    """
    return builtin_conversion[name] if name in builtin_conversion else name

  def arguments(self, name, args):
    """ 
    Build the list of arguments.
     - Take the address of variables for reference parameters.
     - Don't dereference references for reference parameters.
     - Take the address of array elements whether var or ref.
    """
    new = []
    for (i, x) in enumerate(args):
      arg = None
      
      t = self.sig.lookup_param_type(name, i)
      if t == T_REF_SINGLE:
        assert isinstance(x, ast.ExprSingle)

        # For single variables, take the address if they are not ref
        if isinstance(x.elem, ast.ElemId):
          if x.elem.symbol.type == T_VAR_SINGLE:
            arg = '&'+x.elem.name
          elif x.elem.symbol.type == T_REF_SINGLE:
            arg = x.elem.name

        # For subscripts, take their address
        elif isinstance(x.elem, ast.ElemSub):
          if x.elem.symbol.type == T_VAR_ARRAY:
            arg = '&{}'.format(self.elem(x))
          elif x.elem.symbol.type == T_REF_ARRAY:
            arg = '&{}'.format(self.elem(x))
        else:
          assert 0
      
      new.append(arg if arg else self.expr(x))
    return ', '.join(new)

  def header(self):
    """ 
    Insert inclusions.
    """
    self.out('#include <mpi.h>')
    #self.out('#include <stdlib.h>')
    self.out('#include <stdio.h>')
    self.out('#include <syscall.h>')
    self.out('#include "device.h"')
    self.out('#include "runtime/mpi/system.h"')
    self.out('#include "runtime/mpi/source.h"')
    self.out('#include "system/definitions.h"')
    self.out('#include "system/mpi/definitions.h"')
    self.out('#include "system/mpi/builtins.h"')
    self.out('')

  def create_main(self):
    self.out(MAIN_FUNCTION)

  # Program ============================================

  def walk_program(self, node):

    # Walk the entire program
    self.header()
    
    # Declarations
    [self.out(self.decl(x)) for x in node.decls]
    if len(node.decls) > 0:
      self.out('')
    
    # Definitions
    [self.prototype(p) for p in node.defs]
    self.out('')
    [self.definition(p) for p in node.defs]
   
    # Output the buffered blocks
    self.blocker.output()
  
  # Variable declarations ===============================

  def decl(self, node):
    if node.type == T_VAR_ARRAY:
      return 'int {}[{}];'.format(node.name, self.expr(node.expr))
    elif node.type == T_REF_ARRAY:
      return 'int *'+node.name+';'
    elif node.type == T_VAR_SINGLE:
      return 'int '+node.name+';'
    elif node.type == T_VAL_SINGLE:
      return '#define '+node.name+' {}'.format(self.expr(node.expr))
    elif node.type == T_CHANEND_SINGLE:
      return 'chanend'
    elif node.type == T_CHAN_SINGLE:
      return 'chan'
    elif node.type == T_CHAN_ARRAY:
      return 'chanarray'
    else:
      assert 0

  # Procedure declarations ==============================

  def prototype(self, node):
    s = ''
    s += 'void' if node.type == T_PROC else 'int'
    s += ' {}({});'.format(self.procedure_name(node.name),
        ', '.join([self.param(x) for x in node.formals]))
    self.out(s)

  def definition(self, node):
    s = ''
    s += 'void' if node.type == T_PROC else 'int'
    s += ' {}({}){}'.format(self.procedure_name(node.name),
        ', '.join([self.param(x) for x in node.formals]),
        ';' if not node.stmt else '')
    self.parent = node.name
    self.out(s)

    if node.stmt:
      self.blocker.begin()
      [self.out(self.decl(x)) for x in node.decls]
      self.stmt_block(node.stmt)
      self.blocker.end()
    
    self.out('')
  
  # Formals =============================================
  
  def param(self, node):
    if node.type == T_VAL_SINGLE:
      return 'int '+node.name
    elif node.type == T_REF_SINGLE:
      return 'int *'+node.name
    elif node.type == T_REF_ARRAY:
      return 'int '+node.name+'[]'
    elif node.type == T_CHANEND_SINGLE:
      return 'unsigned '+node.name
    else:
      assert 0
  
  # Statements ==========================================

  def stmt_seq(self, node):
    self.blocker.begin()
    for x in node.children(): 
      self.stmt(x)
    self.blocker.end()

  def stmt_par(self, node):
    """ 
    Generate a parallel block.
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
      self.procedure_name(node.name), 
      self.arguments(node.name, node.args)))

  def stmt_ass(self, node):
    self.out('{} = {};'.format(
      self.elem(node.left), self.expr(node.expr)))

  def stmt_in(self, node):
    self.out('{} ? {};'.format(
      self.elem(node.left), self.expr(node.expr)))

  def stmt_out(self, node):
    self.out('{} ! {};'.format(
      self.elem(node.left), self.expr(node.expr)))

  def stmt_alias(self, node):
    self.out('{} = {};'.format(
      self.elem(node.left), self.elem(node.slice)))

  def stmt_connect(self, node):
    if node.core:
      self.out('connect master')
    else:
      self.out('connect slave')

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
    self.out('for ({0} = {1}; {0} < ({1}+{2}); {0}++)'.format(
      node.index.name, self.expr(node.index.base), 
      self.expr(node.index.count)))
    self.stmt_block(node.stmt)

  def stmt_rep(self, node):
    pass

  def stmt_on(self, node):
    """ 
    Generate an on statement.
    """
    self.out('on statement') 

  def stmt_return(self, node):
    self.out('return {};'.format(self.expr(node.expr)))

  # Expressions =========================================

  def expr_single(self, node):
    return self.elem(node.elem)

  def expr_unary(self, node):
    return '({}{})'.format(
        op_conversion[node.op], self.elem(node.elem))

  def expr_binop(self, node):
    return '{} {} {}'.format(self.elem(node.elem), 
        op_conversion[node.op], self.expr(node.right))
  
  # Elements= ===========================================

  def elem_group(self, node):
    return '({})'.format(self.expr(node.expr))

  def elem_sub(self, node):
    return '{}[{}]'.format(node.name, self.expr(node.expr))

  def elem_slice(self, node):
    # If source is an array take the address, if a reference then just the value
    address = ''+node.name
    if node.symbol.type == T_VAR_ARRAY:
      address = '&'+address
    return '({} + {})'.format(address, self.expr(node.base))

  def elem_fcall(self, node):
    return '{}({})'.format(self.procedure_name(node.name), 
        self.arguments(node.name, node.args))

  def elem_number(self, node):
    return '{}'.format(node.value)

  def elem_boolean(self, node):
    return '{}'.format(node.value.upper())

  def elem_string(self, node):
    return '{}'.format(node.value)

  def elem_char(self, node):
    return '{}'.format(node.value)

  def elem_id(self, node):
    #print('{} {}'.format(node.symbol.type, node.name))
    if node.symbol.type == T_REF_SINGLE:
      return '*'+node.name
    else:
      return node.name

