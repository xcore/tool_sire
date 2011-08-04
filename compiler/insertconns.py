# Copyright (c) 2011, James Hanlon, All rights reserved
# This software is freely distributable under a derivative of the
# University of Illinois/NCSA Open Source License posted in
# LICENSE.txt and at <http://github.xcore.com/>

import math

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

  def gen_single_conn(self, tab, chanids, base, chan):
    """
    Generate a connection for a single channel declaration. 'chan' is a
    ChanElemSet with one element.
    """
    elem = chan.elems[0]
    location = None
    if elem.master:
      location = ast.ExprSingle(ast.ElemNumber(
        tab.lookup_slave_location(chan.name, elem.index)))
    chanend = ast.ElemId(chan.chanend)
    chanend.symbol = Symbol(chan.chanend, T_CHANEND_SINGLE, 
        None, scope=T_SCOPE_PROC)
    chanid = ast.ExprSingle(ast.ElemNumber(chanids[chan.name]))
    return ast.StmtConnect(chanend, chanid, location)

  def gen_array_conn(self, tab, chanids, base, chan):
    """
    Generate a conncection for an array channel declaration. We must analyse
    the subscript by generating nested conditional statements. 'chan' is a
    ChanElemSet with multiple elements.
    """
    
    def create_single_connection(s, chan, index, master):
      self.debug('New connection for index {}'.format(index))
      location = None
      if master:
        location = ast.ExprSingle(ast.ElemNumber(
            tab.lookup_slave_location(chan.name, index)))
      chanend = ast.ElemId(chan.chanend)
      chanend.symbol = Symbol(chan.chanend, T_CHANEND_SINGLE, None, scope=T_SCOPE_PROC)
      chanid = ast.ExprSingle(ast.ElemNumber(chanids[chan.name]))
      cond = ast.ExprBinop('=', ast.ElemGroup(chan.expr), ast.ElemNumber(index))
      conn = ast.StmtConnect(chanend, chanid, location)
      return ast.StmtIf(cond, conn, s) if s else conn

    def create_range_connection(s, chan, begin, end, master, difference):
      self.debug('New connection over range {} to {}'.format(begin, end))
      if master:
        offset_expr = ast.ExprSingle(ast.ElemNumber(math.floor(math.fabs(difference))))
        offset_expr = ast.ExprUnary('-', offset_expr) if difference<0 else offset_expr
        offset_expr = ast.ExprBinop('+', ast.ElemGroup(chan.expr), offset_expr)
        location = form_location(self.sym, base, offset_expr, 1)
      else:
        location = None
      chanend = ast.ElemId(chan.chanend)
      chanend.symbol = Symbol(chan.chanend, T_CHANEND_SINGLE, None, scope=T_SCOPE_PROC)
      chanid = ast.ExprSingle(ast.ElemNumber(chanids[chan.name]))
      cond = ast.ExprBinop('and', 
          ast.ElemGroup(ast.ExprBinop('>=', ast.ElemGroup(chan.expr),
            ast.ExprSingle(ast.ElemNumber(min(begin, end))))),
          ast.ExprBinop('<=', ast.ElemGroup(chan.expr),
            ast.ExprSingle(ast.ElemNumber(max(begin, end)))))
      conn = ast.StmtConnect(chanend, chanid, location)
      return ast.StmtIf(cond, conn, s) if s else conn

    def index_offset_diff(name, index, master, location):
      return (tab.lookup_slave_location(name, index) - location if master else None)

    # Sort the channel elements into increasing index
    chan.elems = sorted(chan.elems, key=lambda x: x.index)

    # Build a list of channel index ranges
    x = chan.elems[0] 
    l = [[x, x]]
    location = base.elem.value+x.index
    diff = index_offset_diff(chan.name, x.index, x.master, location)
    for x in chan.elems[1:]:
      location = base.elem.value+x.index
      cdiff = index_offset_diff(chan.name, x.index, x.master, location)
      if diff == cdiff:
        l[-1][1] = x
      else:
        diff = cdiff
        l.append([x, x])
  
    # Print them
    if self.print_debug:
      for x in l:
        self.debug('Range: {}'.format(
          ' '.join(['{}'.format(y.index) for y in x])))

    # Construct the connection syntax
    s = None
    for x in reversed(l):
      location = base.elem.value+x[0].index
      if x[0] == x[1]:
        s = create_single_connection(s, chan, x[0].index, x[0].master)
      else:
        s = create_range_connection(s, chan, x[0].index, x[1].index, x[0].master, 
            index_offset_diff(chan.name, x[0].index, x[0].master, location))

    return s

  def insert_connections(self, tab, chanids, stmt, chans, base):
    """
    Insert connections for a process from a list of channel uses (name, index)
    by composing them in sequence, prior to the process. If there are no
    connecitons to be made, just return the process.

    The location expression is formed with a compression factor of 1 because we
    have already applied this when we evaluated the offset.
    """
    if len(chans) > 0:
      conns = []
      for x in chans:
        if len(x.elems) == 1:
          conns.append(self.gen_single_conn(tab, chanids, base, x))
        else:
          conns.append(self.gen_array_conn(tab, chanids, base, x))
      s = ast.StmtSeq(conns + [stmt])
      s.location = stmt.location
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
    self.stmt(node.stmt, node.chantab, node.chanids, decls)
    node.stmt = self.insert_connections(node.chantab, node.chanids, 
        node.stmt, node.chans, node.location)

    # Insert the channel end declarations
    for x in decls:
      d = ast.Decl(x, T_CHANEND_SINGLE, None)
      d.symbol = Symbol(x, T_CHANEND_SINGLE, None, scope=T_SCOPE_PROC)
      node.decls.append(d)

    self.debug('[def connections]:')
    if self.print_debug:
      self.display_chans(node.chans)
  
  # Statements ==========================================

  # Top-level statements where connections are inserted

  def stmt_rep(self, node, tab, chanids, decls):
    self.debug('[rep connections]:')
    if self.print_debug:
      self.display_chans(node.chans)
    self.stmt(node.stmt, tab, chanids, decls)
    node.stmt = self.insert_connections(tab, chanids, node.stmt, node.chans,
        node.location)
    decls.extend([x.chanend for x in node.chans])

  def stmt_par(self, node, tab, chanids, decls):
    self.debug('[par connections]:')
    for (i, (x, y)) in enumerate(zip(node.stmt, node.chans)):
      self.debug('[par stmt]: ')
      self.stmt(x, tab, chanids, decls) 
      node.stmt[i] = self.insert_connections(tab, chanids, node.stmt[i], y,
          node.location)
      decls.extend([z.chanend for z in y])
      if self.print_debug:
        self.display_chans(y)
 
  # Other statements containing processes

  def stmt_seq(self, node, tab, chanids, decls):
    [self.stmt(x, tab, chanids, decls) for x in node.stmt]

  def stmt_if(self, node, tab, chanids, decls):
    self.stmt(node.thenstmt, tab, chanids, decls)
    self.stmt(node.elsestmt, tab, chanids, decls)

  def stmt_while(self, node, tab, chanids, decls):
    self.stmt(node.stmt, tab, chanids, decls)

  def stmt_for(self, node, tab, chanids, decls):
    self.stmt(node.stmt, tab, chanids, decls)

  def stmt_on(self, node, tab, chanids, decls):
    self.stmt(node.stmt, tab, chanids, decls)

  # Other statements

  def stmt_in(self, node, tab, chanids, decls):
    pass

  def stmt_out(self, node, tab, chanids, decls):
    pass

  def stmt_pcall(self, node, tab, chanids, decls):
    pass
    
  def stmt_ass(self, node, tab, chanids, decls):
    pass

  def stmt_alias(self, node, tab, chanids, decls):
    pass

  def stmt_skip(self, node, tab, chanids, decls):
    pass

  def stmt_connect(self, node, tab, chanids, decls):
    pass

  def stmt_assert(self, node, tab, chanids, decls):
    pass

  def stmt_return(self, node, tab, chanids, decls):
    pass

