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
    master = tab.is_master(chan.name, elem.index, elem.location)
    location = None
    if master:
      location = ast.ExprSingle(ast.ElemNumber(
        tab.lookup_slave_location(chan.name, elem.index)))
    else:
      location = ast.ExprSingle(ast.ElemNumber(
        tab.lookup_master_location(chan.name, elem.index)))
    chanend = ast.ElemId(chan.chanend)
    chanend.symbol = Symbol(chan.chanend, T_CHANEND_SINGLE, 
        None, scope=T_SCOPE_PROC)
    chanid = ast.ExprSingle(ast.ElemNumber(chanids[chan.name]))
    return ast.StmtConnect(chanend, chanid, location, master)

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
      else:
        location = ast.ExprSingle(ast.ElemNumber(
          tab.lookup_master_location(chan.name, index)))
      chanend = ast.ElemId(chan.chanend)
      chanend.symbol = Symbol(chan.chanend, T_CHANEND_SINGLE, None, scope=T_SCOPE_PROC)
      chanid = ast.ExprSingle(ast.ElemNumber(chanids[chan.name]))
      cond = ast.ExprBinop('=', ast.ElemGroup(chan.expr), ast.ElemNumber(index))
      conn = ast.StmtConnect(chanend, chanid, location, master)
      return ast.StmtIf(cond, conn, s) if s else conn

    def create_range_connection(s, chan, begin, end, master, difference):
      self.debug('New connection over range {} to {}'.format(begin, end))
      offset_expr = ast.ExprSingle(ast.ElemNumber(math.floor(math.fabs(difference))))
      offset_expr = ast.ExprUnary('-', offset_expr) if difference<0 else offset_expr
      offset_expr = ast.ExprBinop('+', ast.ElemGroup(chan.expr), offset_expr)
      location = form_location(self.sym, base, offset_expr, 1)
      chanend = ast.ElemId(chan.chanend)
      chanend.symbol = Symbol(chan.chanend, T_CHANEND_SINGLE, None, scope=T_SCOPE_PROC)
      chanid = ast.ExprSingle(ast.ElemNumber(chanids[chan.name]))
      cond = ast.ExprBinop('and', 
          ast.ElemGroup(ast.ExprBinop('>=', ast.ElemGroup(chan.expr),
            ast.ExprSingle(ast.ElemNumber(min(begin, end))))),
          ast.ExprBinop('<=', ast.ElemGroup(chan.expr),
            ast.ExprSingle(ast.ElemNumber(max(begin, end)))))
      conn = ast.StmtConnect(chanend, chanid, location, master)
      return ast.StmtIf(cond, conn, s) if s else conn

    def target_loc(name, index, loc):
      if tab.is_master(name, index, loc):
        return tab.lookup_slave_location(name, index)
      else:
        return tab.lookup_master_location(name, index)

    # Sort the channel elements into increasing index
    chan.elems = sorted(chan.elems, key=lambda x: x.index)

    # Build a list of channel index ranges
    x = chan.elems[0] 
    l = [[x, x]]
    loc = base.elem.value + x.index
    diff = target_loc(chan.name, x.index, loc) - loc
    master = tab.is_master(chan.name, x.index, loc)
    for x in chan.elems[1:]:
      loc = base.elem.value + x.index
      cdiff = target_loc(chan.name, x.index, loc) - loc
      cmaster = tab.is_master(chan.name, x.index, loc)
      if diff == cdiff and master == cmaster:
        l[-1][1] = x
      else:
        diff = cdiff
        master = cmaster
        l.append([x, x])
  
    # Print them
    if self.print_debug:
      for x in l:
        self.debug('Range: {}'.format(
          ' '.join(['{}'.format(y.index) for y in x])))

    # Construct the connection syntax
    s = None
    for x in reversed(l):
      loc = base.elem.value + x[0].index
      master = tab.is_master(chan.name, x[0].index, x[0].location)
      if x[0] == x[1]:
        s = create_single_connection(s, chan, x[0].index, master)
      else:
        s = create_range_connection(s, chan, x[0].index, x[1].index, master, 
            target_loc(chan.name, x[0].index, loc) - loc)

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

