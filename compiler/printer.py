# Copyright (c) 2010, James Hanlon, All rights reserved
# This software is freely distributable under a derivative of the
# University of Illinois/NCSA Open Source License posted in
# LICENSE.txt and at <http://github.xcore.com/>

import sys

import ast
from walker import NodeWalker
from definitions import *
from typedefs import *

INDENT = '  '
NO_INDENT = ''

class Printer(NodeWalker):
  """ 
  A walker class to pretty-print the AST in the langauge syntax.
  """
  def __init__(self, buf=sys.stdout, labels=False):
    super(Printer, self).__init__()
    self.buf = buf
    self.labels = labels
    self.indent = []

  def indt(self):
    """ 
    Produce an indent. If its the first statement of a seq or par block we
    only produce a single space.
    """
    if len(self.indent) > 0:
      if self.indent[-1] == NO_INDENT:
        return ''
      else:
        return INDENT*(len(self.indent))
        #return ''.join([x for x in self.indent])
    return ''
  
  def out(self, s):
    """ 
    Write an indented line.
    """
    self.buf.write(self.indt()+s)

  def arg_list(self, args):
    return ', '.join([self.expr(x) for x in args])

  def var_decls(self, decls):
    self.buf.write((self.indt() if len(decls)>0 else '')
        +(';\n'+self.indt()).join(
        [self.decl(x) for x in decls]))
    if len(decls)>0: self.buf.write(';\n')
  
  def display_location(self, stmt):
    if self.labels and hasattr(stmt, 'location') and not stmt.location==None:
        self.out('@({})\n'.format(self.expr(stmt.location)))
  
  # Program ============================================

  def walk_program(self, node):
    
    # Program declarations
    self.var_decls(node.decls)
    self.buf.write('\n')

    # Program definitions (procedures)
    [self.defn(x, 0) for x in node.defs]
  
  # Variable declarations ===============================

  def decl(self, node):
    
    if node.type == T_VAL_SINGLE:
      return 'val {} := {}'.format(node.name, self.expr(node.expr))
    
    if node.type == T_VAR_SINGLE:
      return 'var {}'.format(node.name)
    
    elif node.type == T_VAR_ARRAY:
      return 'var {}[{}]'.format(node.name, self.expr(node.expr))
    
    elif node.type == T_REF_ARRAY:
      return node.name+'[]'
   
    elif node.type == T_CHAN_SINGLE:
      return 'chan '+node.name

    elif node.type == T_CHAN_ARRAY:
      return 'chan '+node.name+'[{}]'.format(self.expr(node.expr))

    elif node.type == T_CHANEND_SINGLE:
      return 'chanend '+node.name

    elif node.type == T_CHANEND_ARRAY:
      return 'chanend '+node.name+'[{}]'.format(self.expr(node.expr))

    else:
      assert 0

  # Procedure declarations ==============================

  def defn(self, node, d):
    
    # Procedure definition
    name = node.name if node.name != '_main' else 'main'
    self.buf.write('{} {}({})'.format(node.type.specifier, name, 
        ', '.join([self.param(x) for x in node.formals])))
    
    # If it is a prototype
    if not node.stmt:
      self.buf.write(';\n\n')
    else:
      self.buf.write(' is\n')
      
      # Procedure declarations
      self.indent.append(INDENT)
      self.var_decls(node.decls)

      # Statement block
      if (isinstance(node.stmt, ast.StmtPar) 
          or isinstance(node.stmt, ast.StmtSeq)):
        self.indent.pop()
        self.display_location(node.stmt)
        self.stmt(node.stmt)
        self.buf.write('\n\n')
      else:
        self.display_location(node.stmt)
        self.stmt(node.stmt)
        self.buf.write('\n\n')
        self.indent.pop()
  
  # Formals =============================================
  
  def param(self, node):
    if node.type == T_VAL_SINGLE:
      return 'val '+node.name
    elif node.type == T_REF_SINGLE:
      return 'var '+node.name
    elif node.type == T_REF_ARRAY:
      return 'var {}[{}]'.format(node.name, self.expr(node.expr))
    elif node.type == T_CHANEND_SINGLE:
      return 'chanend {}'.format(node.name)
    elif node.type == T_CHANEND_ARRAY:
      return 'chanend {}[{}]'.format(node.name, self.expr(node.expr))
    elif node.type == T_CHAN_SINGLE:
      return 'chan {}'.format(node.name)
    elif node.type == T_CHAN_ARRAY:
      return 'chan {}[{}]'.format(node.name, self.expr(node.expr))
    else:
      assert 0

  # Statements ==========================================

  def stmt_block(self, node, sep):
    """
    Output a block of statements. E.g.::
      { 
      stmt1;
      stmt2;
      { stmt3||
        stmt4
      };
      stmt5
      }
    """
    self.out('{\n')
    self.indent.append(INDENT)
    for (i, x) in enumerate(node.stmt): 
      if sep=='||':
        self.stmt(x)
      else:
        self.stmt(x)
      self.buf.write(sep if i<(len(node.stmt)-1) else '')
      self.buf.write('\n')
    self.indent.pop()
    self.out('}')

  def stmt_seq(self, node):
    self.stmt_block(node, ';')

  def stmt_par(self, node):
    self.stmt_block(node, '||')

  def stmt_server(self, node):
    self.out('server({})\n'.format(', '.join(
        [self.param(x) for x in node.decls])))
    self.indent.append(INDENT)
    self.stmt(node.server)
    self.indent.pop()
    self.out('\n')
    self.indent.append(INDENT)
    self.stmt(node.client)
    self.indent.pop()

  def stmt_skip(self, node):
    self.out('skip')

  def stmt_pcall(self, node):
    self.out('{}({})'.format(
      node.name, self.arg_list(node.args)))

  def stmt_ass(self, node):
    self.out('{} := {}'.format(
      self.elem(node.left), self.expr(node.expr)))

  def stmt_in(self, node):
    self.out('{} ? {}'.format(
      self.elem(node.left), self.expr(node.expr)))

  def stmt_out(self, node):
    self.out('{} ! {}'.format(
      self.elem(node.left), self.expr(node.expr)))

  def stmt_alias(self, node):
    self.out('{} aliases {}'.format(
      self.elem(node.left), self.elem(node.slice)))

  def stmt_connect(self, node):
    if node.type == CONNECT_MASTER:
      self.out('connect {}:{} to slave {}'.format(self.elem(node.left), 
        self.expr(node.id), self.expr(node.expr)))
    elif node.type == CONNECT_SLAVE:
      self.out('connect {}:{} to master {}'.format(self.elem(node.left), 
        self.expr(node.id), self.expr(node.expr)))
    elif node.type == CONNECT_CLIENT:
      self.out('connect {}:{} to server {}'.format(self.elem(node.left), 
        self.expr(node.id), self.expr(node.expr)))
    elif node.type == CONNECT_SERVER:
      self.out('connect {}:{} to client'.format(self.elem(node.left), 
        self.expr(node.id)))
    else:
      assert 0

  def stmt_if(self, node):
    self.out('if {}\n'.format(self.expr(node.cond)))
    self.out('then\n')
    self.indent.append(INDENT)
    self.stmt(node.thenstmt) ; self.buf.write('\n')
    self.indent.pop()
    self.out('else\n')
    self.indent.append(INDENT)
    self.stmt(node.elsestmt)
    self.indent.pop()

  def stmt_while(self, node):
    self.out('while {} do\n'.format(self.expr(node.cond)))
    self.indent.append(INDENT)
    self.stmt(node.stmt)
    self.indent.pop()

  def stmt_for(self, node):
    self.out('for {} do\n'.format(self.elem(node.index)))
    self.indent.append(INDENT)
    self.stmt(node.stmt)
    self.indent.pop()

  def stmt_rep(self, node):
    self.out('par {} do\n'.format(
      ', '.join([self.elem(x) for x in node.indicies]))) 
    self.indent.append(INDENT)
    self.display_location(node.stmt)
    self.stmt(node.stmt)
    self.indent.pop()

  def stmt_on(self, node):
    self.out('on {} do\n'.format(self.expr(node.expr)))
    self.indent.append(INDENT)
    # NOTE: This location won't show where we have made substitutions in 
    # transform par and rep and we hav'nt updated the location labels.
    self.display_location(node.stmt)
    self.stmt(node.stmt)
    self.indent.pop()

  def stmt_assert(self, node):
    self.out('assert {}'.format(self.expr(node.expr)))

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
    return '{}[{} for {}]'.format(node.name, 
        self.expr(node.base), self.expr(node.count))

  def elem_index_range(self, node):
    return '{} in [{} for {}]'.format(node.name, 
        self.expr(node.base), self.expr(node.count))

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

