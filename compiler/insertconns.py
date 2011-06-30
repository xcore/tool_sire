# Copyright (c) 2011, James Hanlon, All rights reserved
# This software is freely distributable under a derivative of the
# University of Illinois/NCSA Open Source License posted in
# LICENSE.txt and at <http://github.xcore.com/>

import ast
from walker import NodeWalker
from definitions import PROC_ID_VAR
from typedefs import *
from symbol import Symbol
from formlocation import form_location

from printer import Printer

class InsertConns(NodeWalker):
  """
  Propagate the expanded channel uses up to replicator or composition level and
  insert the corresponding connections. For each connection set (for a single
  channel or subscripted array) allocate a new channel end which is declared in
  the procedure scope.
  """
  def __init__(self, sym, print_debug=False):
    self.sym = sym
    self.print_debug = print_debug

  def debug(self, s):
    if self.print_debug:
      print(s)

  def insert_connections(self, tab, stmt, chans):
    """
    Insert connections for a process from a list of channel uses (name, index)
    by composing them in sequence, prior to the process. If there are no
    connecitons to be made, just return the process.

    The location expression is formed with a compression factor of 1 because we
    have already applied this when we evaluated the offset.
    """
    if len(chans) > 0:
      pid = ast.ElemId(PROC_ID_VAR)
      pid.symbol = Symbol(pid.name, T_VAR_SINGLE, scope=T_SCOPE_PROC)
      conns = []
      for x in chans:
        
        # If the expansion is of size one (single or constant subscript)
        if len(x.elems) == 1:
          elem = x.elems[0]
          off = ast.ExprSingle(ast.ElemNumber(
              tab.slave_offset(x.name, elem.index)))
          loc = form_location(self.sym, pid, off, 1) if elem.master else None
          chanend = ast.ElemId(x.chanend)
          chanend.symbol = Symbol(x.chanend, T_CHANEND_SINGLE, 
              None, scope=T_SCOPE_PROC)
          conns.append(ast.StmtConnect(chanend, loc))

        # Otherwise we must analyse the subscript
        else:
          s = ast.StmtSkip()
          for y in reversed(x.elems):
            cond = ast.ExprBinop('=', ast.ElemGroup(x.expr),
                ast.ElemNumber(y.index))
            off = ast.ExprSingle(ast.ElemNumber(
                tab.slave_offset(x.name, y.index)))
            loc = form_location(self.sym, pid, off, 1) if y.master else None
            chanend = ast.ElemId(x.chanend)
            chanend.symbol = Symbol(x.chanend, T_CHANEND_SINGLE, 
                None, scope=T_SCOPE_PROC)
            conn = ast.StmtConnect(chanend, loc)
            s = ast.StmtIf(cond, conn, s)
          conns.append(s)

      s = ast.StmtSeq(conns + [stmt])
      s.offset = stmt.offset
      return s
    else:
      return stmt

  def display_chans(self, chans):
    for x in chans:
      if x.expr:
        print('  {}[{}]'.format(x.name, Printer().expr(x.expr)))
      else:
        print('  {}'.format(x.name))
      for y in x.elems:
        if y.master:
          print('    connect {} to {}'.format(
            '{}[{}]'.format(x.name, y.index) if x.expr!=None else x.name, '?'))
        else:
          print('    connect {}'.format(
            '{}[{}]'.format(x.name, y.index) if x.expr!=None else x.name, '?'))

  # Program ============================================

  def walk_program(self, node):
    [self.defn(x) for x in node.defs]
  
  # Procedure definitions ===============================

  def defn(self, node):
    self.debug('Inserting connections for: '+node.name)
    decls = []
    decls.extend([x.chanend for x in node.chans])
    self.stmt(node.stmt, node.chantab, decls)
    node.stmt = self.insert_connections(node.chantab, node.stmt, node.chans)

    # Insert the channel end declarations
    for x in decls:
      d = ast.Decl(x, T_CHANEND_SINGLE, None)
      d.symbol = Symbol(x, T_CHANEND_SINGLE, None, scope=T_SCOPE_PROC)
      node.decls.append(d)

    self.debug('[def connections]:')
    if self.print_debug:
      self.self.display_chans(node.chans)
  
  # Statements ==========================================

  # Top-level statements where connections are inserted

  def stmt_rep(self, node, tab, decls):
    self.debug('[rep connections]:')
    if self.print_debug:
      self.display_chans(node.chans)
    self.stmt(node.stmt, tab, decls)
    node.stmt = self.insert_connections(tab, node.stmt, node.chans)
    decls.extend([x.chanend for x in node.chans])

  def stmt_par(self, node, tab, decls):
    self.debug('[par connections]:')
    for (i, (x, y)) in enumerate(zip(node.stmt, node.chans)):
        self.debug('[par stmt]: ')
        self.stmt(x, tab, decls) 
        node.stmt[i] = self.insert_connections(tab, node.stmt[i], y)
        decls.extend([z.chanend for z in y])
        if self.print_debug:
          self.display_chans(y)
 
  # Other statements containing processes

  def stmt_seq(self, node, tab, decls):
    [self.stmt(x, tab, decls) for x in node.stmt]

  def stmt_if(self, node, tab, decls):
    self.stmt(node.thenstmt, tab, decls)
    self.stmt(node.elsestmt, tab, decls)

  def stmt_while(self, node, tab, decls):
    self.stmt(node.stmt, tab, decls)

  def stmt_for(self, node, tab, decls):
    self.stmt(node.stmt, tab, decls)

  # Other statements

  def stmt_in(self, node, tab, decls):
    pass

  def stmt_out(self, node, tab, decls):
    pass

  def stmt_pcall(self, node, tab, decls):
    pass
    
  def stmt_ass(self, node, tab, decls):
    pass

  def stmt_alias(self, node, tab, decls):
    pass

  def stmt_skip(self, node, tab, decls):
    pass

  def stmt_return(self, node, tab, decls):
    pass

  # Prohibited statements

  def stmt_on(self, node, tab, decls):
    assert 0

  def stmt_connect(self, node, tab, decls):
    assert 0

