# Copyright (c) 2011, James Hanlon, All rights reserved
# This software is freely distributable under a derivative of the
# University of Illinois/NCSA Open Source License posted in
# LICENSE.txt and at <http://github.xcore.com/>

import math

import ast
from walker import NodeWalker
from definitions import *
from typedefs import *
from symboltab import Symbol
from formlocation import form_location
from printer import Printer
from indicies import indicies_value, indicies_expr

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

  def chanend_type(self, chan):
    """
    Given a 'chan' ChanElemSet return the corresponding chanend type.
    """
    if chan.symbol.scope == T_SCOPE_PROC or chan.symbol.scope == T_SCOPE_FUNC:
      return T_CHANEND_SINGLE
    elif chan.symbol.scope == T_SCOPE_SERVER:
      return T_CHANEND_SERVER_SINGLE
    elif chan.symbol.scope == T_SCOPE_CLIENT:
      return T_CHANEND_CLIENT_SINGLE
    else:
      assert 0

  def connect_type(self, chan, master):
    """
    Given a 'chan' ChanElemSet, scope type and whether the connect is a master
    or slave, return the resulting type of the connect statement.
    """
    if chan.symbol.scope == T_SCOPE_PROC or chan.symbol.scope == T_SCOPE_FUNC:
      return CONNECT_MASTER if master else CONNECT_SLAVE
    elif chan.symbol.scope == T_SCOPE_SERVER:
        return CONNECT_SERVER
    elif chan.symbol.scope == T_SCOPE_CLIENT:
        return CONNECT_CLIENT
    else:
      assert 0

  def gen_single_conn(self, tab, chan):
    """
    Generate a connection for a single channel declaration. 'chan' is a
    ChanElemSet with one element.
    """
    elem = chan.elems[0]
    master = tab.is_master(chan.name, elem.index, elem.location)
    connid = tab.lookup(chan.name, elem.index).connid
    location = None
    if master:
      location = ast.ExprSingle(ast.ElemNumber(
          tab.lookup_slave_location(chan.name, elem.index)))
    else:
      location = ast.ExprSingle(ast.ElemNumber(
          tab.lookup_master_location(chan.name, elem.index)))
    chanend = ast.ElemId(chan.chanend)
    chanend.symbol = Symbol(chan.chanend, self.chanend_type(chan), 
        None, scope=T_SCOPE_PROC)
    chanid = ast.ExprSingle(ast.ElemNumber(connid))
    return ast.StmtConnect(chanend, chanid, location, 
        self.connect_type(chan, master))

  def gen_array_conn(self, tab, chan):
    """
    Generate a conncection for an array channel declaration. We must analyse
    the subscript by generating nested conditional statements. 'chan' is a
    ChanElemSet with multiple elements.
    """
    
    def create_single_connection(s, chan, indicies_expr, 
        range_begin, index, master, connid):
      self.debug('New connection for index {}'.format(index))
      if master:
        location = ast.ExprSingle(ast.ElemNumber(
            tab.lookup_slave_location(chan.name, index)))
      else:
        location = ast.ExprSingle(ast.ElemNumber(
            tab.lookup_master_location(chan.name, index)))
      chanend = ast.ElemId(chan.chanend)
      chanend.symbol = Symbol(chan.chanend, self.chanend_type(chan), 
          None, scope=T_SCOPE_PROC)
      chanid = ast.ExprSingle(ast.ElemNumber(connid))
      cond = ast.ExprBinop('=', ast.ElemGroup(indicies_expr), 
          ast.ElemNumber(range_begin))
      conn = ast.StmtConnect(chanend, chanid, location, 
          self.connect_type(chan, master))
      return ast.StmtIf(cond, conn, s) if s else conn

    def create_range_connection(s, chan, indicies_expr, begin, end, master,
        diff, connid):
      self.debug('New connection over range {} to {}'.format(begin, end))
      if diff != 0:
        location = ast.ExprSingle(ast.ElemNumber(math.floor(math.fabs(diff))))
        location = ast.ExprUnary('-', location) if diff<0 else location
        location = ast.ExprBinop('+', ast.ElemGroup(indicies_expr), location)
      else:
        location = indicies_expr
      chanend = ast.ElemId(chan.chanend)
      chanend.symbol = Symbol(chan.chanend, self.chanend_type(chan), 
          None, scope=T_SCOPE_PROC)
      chanid = ast.ExprSingle(ast.ElemNumber(connid))
      cond = ast.ExprBinop('and', 
          ast.ElemGroup(ast.ExprBinop('>=', ast.ElemGroup(indicies_expr),
            ast.ExprSingle(ast.ElemNumber(min(begin, end))))),
          ast.ExprBinop('<=', ast.ElemGroup(indicies_expr),
            ast.ExprSingle(ast.ElemNumber(max(begin, end)))))
      conn = ast.StmtConnect(chanend, chanid, location,
          self.connect_type(chan, master))
      return ast.StmtIf(cond, conn, s) if s else conn

    def target_loc(name, index, master):
      if master:
        return tab.lookup_slave_location(name, index)
      else:
        return tab.lookup_master_location(name, index)

    # Sort the channel elements into increasing order of indicies
    chan.elems = sorted(chan.elems, key=lambda x: x.indicies_value)

    # Build a list of channel index ranges
    self.debug('=====')
    x = chan.elems[0] 
    l = [[x, x]]
    master = tab.is_master(chan.name, x.index, x.location)
    diff = target_loc(chan.name, x.index, master) - x.indicies_value
    self.debug('{}: -> {}[{}]: target {} diff {}'.format(x.indicies_value, 
        chan.name, x.index, target_loc(chan.name, x.index, master), diff))
    for x in chan.elems[1:]:
      cmaster = tab.is_master(chan.name, x.index, x.location)
      cdiff = target_loc(chan.name, x.index, cmaster) - x.indicies_value
      self.debug('{}: {}[{}] -> target {} diff {}'.format(x.indicies_value, 
          chan.name, x.index, target_loc(chan.name, x.index, cmaster), cdiff))
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
    i_expr = indicies_expr(chan.indicies)
    for x in reversed(l):
      master = tab.is_master(chan.name, x[0].index, x[0].location)
      connid = tab.lookup(chan.name, x[0].index).connid
      if x[0] == x[1]:
        s = create_single_connection(s, chan, i_expr, x[0].indicies_value, 
            x[0].index, master, connid)
      else:
        diff = (target_loc(chan.name, x[0].index, master) -
            x[0].indicies_value)
        s = create_range_connection(s, chan, i_expr, x[0].indicies_value,
            x[1].indicies_value, master, diff, connid)

    return s

  def insert_connections(self, tab, stmt, chans):
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
          conns.append(self.gen_single_conn(tab, x))
        else:
          conns.append(self.gen_array_conn(tab, x))
      if len(conns) > 1:
        s1 = ast.StmtPar(conns) 
        s1.location = stmt.location
        s1.chans = []
        s2 = ast.StmtSeq([s1, stmt])
        s2.location = stmt.location
        s2.chans = []
        return s2
      else:
        s = ast.StmtSeq(conns+[stmt])
        s.location = stmt.location
        s.chans = []
        return s
    else:
      return stmt

  def create_decls(self, chans):
    decls = []
    for x in chans:
      
      if x.symbol.scope == T_SCOPE_PROC or x.symbol.scope == T_SCOPE_FUNC:
        d = ast.Decl(x.chanend, T_CHANEND_SINGLE, None)
        d.symbol = Symbol(x.chanend, T_CHANEND_SINGLE, None, scope=T_SCOPE_PROC)
        decls.append(d)
      
      elif x.symbol.scope == T_SCOPE_SERVER:
        d = ast.Decl(x.chanend, T_CHANEND_SERVER_SINGLE, None)
        d.symbol = Symbol(x.chanend, T_CHANEND_SERVER_SINGLE, None,
            scope=T_SCOPE_SERVER)
        decls.append(d)
      
      elif x.symbol.scope == T_SCOPE_CLIENT:
        d = ast.Decl(x.chanend, T_CHANEND_CLIENT_SINGLE, None)
        d.symbol = Symbol(x.chanend, T_CHANEND_CLIENT_SINGLE, None,
            scope=T_SCOPE_CLIENT)
        decls.append(d)
      
      else:
        assert 0
    return decls

  # Program ============================================

  def walk_program(self, node):
    [self.defn(x) for x in node.defs]
  
  # Procedure definitions ===============================

  def defn(self, node):
    self.debug('Inserting connections for: '+node.name)
    decls = self.create_decls(node.chans)
    self.stmt(node.stmt, node.chantab, decls)
    node.stmt = self.insert_connections(node.chantab, node.stmt, node.chans)

    # Insert the channel end declarations
    #for x in decls:
    #  d = ast.Decl(x, T_CHANEND_SINGLE, None)
    #  d.symbol = Symbol(x, T_CHANEND_SINGLE, None, scope=T_SCOPE_PROC)
    #  node.decls.append(d)
    node.decls += decls

    if self.print_debug:
      self.debug('[def connections]:')
      self.display_chans(node.chans)
  
  # Statements ==========================================

  # Top-level statements where connections are inserted

  def stmt_rep(self, node, tab, decls):
    if self.print_debug:
      self.debug('[rep connections]:')
      self.display_chans(node.chans)
    self.stmt(node.stmt, tab, decls)
    node.stmt = self.insert_connections(tab, node.stmt, node.chans)
    decls += self.create_decls(node.chans)

  def stmt_par(self, node, tab, decls):
    self.debug('[par connections]:')
    for (i, (x, y)) in enumerate(zip(node.stmt, node.chans)):
      self.debug('[process {}]: '.format(i))
      self.stmt(x, tab, decls) 
      node.stmt[i] = self.insert_connections(tab, node.stmt[i], y)
      decls += self.create_decls(y)
      if self.print_debug:
        self.display_chans(y)

  def stmt_server(self, node, tab, decls):
    self.debug('[server connections]:')
    self.stmt(node.server, tab, decls)
    node.server = self.insert_connections(tab, node.server, node.chans[0])
    decls += self.create_decls(node.chans[0])
    if self.print_debug:
      self.display_chans(node.chans[0])
    self.debug('[client connections]:')
    self.stmt(node.client, tab, decls)
    node.client = self.insert_connections(tab, node.client, node.chans[1])
    decls += self.create_decls(node.chans[1])
    if self.print_debug:
      self.display_chans(node.chans[1])

  def stmt_on(self, node, tab, decls):
    if self.print_debug:
      self.debug('[on connections]:')
      self.display_chans(node.chans)
    self.stmt(node.stmt, tab, decls)
    node.stmt = self.insert_connections(tab, node.stmt, node.chans)
    decls += self.create_decls(node.chans)

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

  def stmt_connect(self, node, tab, decls):
    pass

  def stmt_assert(self, node, tab, decls):
    pass

  def stmt_return(self, node, tab, decls):
    pass

