# Copyright (c) 2011, James Hanlon, All rights reserved
# This software is freely distributable under a derivative of the
# University of Illinois/NCSA Open Source License posted in
# LICENSE.txt and at <http://github.xcore.com/>

import math

import ast
from util import debug
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
  def __init__(self, sym, debug=False):
    self.sym = sym
    self.debug = debug

  def chanend_type(self, chan):
    """
    Given a 'chan' ChanElemSet return the corresponding chanend type.
    """
    if chan.symbol.scope == T_SCOPE_PROC:
      return T_CHANEND_SINGLE
    if chan.symbol.scope == T_SCOPE_BLOCK:
      return T_CHANEND_SINGLE
    elif chan.symbol.scope == T_SCOPE_SERVER:
      return T_CHANEND_SERVER_SINGLE
    elif chan.symbol.scope == T_SCOPE_CLIENT:
      return T_CHANEND_CLIENT_SINGLE
    else:
      print(chan.symbol.scope)
      assert 0

  def connect_type(self, chan, master):
    """
    Given a 'chan' ChanElemSet, scope type and whether the connect is a master
    or slave, return the resulting type of the connect statement.
    """
    if chan.symbol.scope == T_SCOPE_PROC:
      return CONNECT_MASTER if master else CONNECT_SLAVE
    if chan.symbol.scope == T_SCOPE_BLOCK:
      return CONNECT_MASTER if master else CONNECT_SLAVE
    elif chan.symbol.scope == T_SCOPE_SERVER:
        return CONNECT_SERVER
    elif chan.symbol.scope == T_SCOPE_CLIENT:
        return CONNECT_CLIENT
    else:
      print(chan.symbol.scope)
      assert 0

  def gen_single_conn(self, tab, scope, chan):
    """
    Generate a connection for a single channel declaration. 'chan' is a
    ChanElemSet with one element.
    """
    elem = chan.elems[0]
    master = tab.lookup_is_master(chan.name, elem.index, elem.location, scope)
    connid = tab.lookup(chan.name, elem.index, scope).connid
    location = None
    if master:
      location = ast.ExprSingle(ast.ElemNumber(
          tab.lookup_slave_location(chan.name, elem.index, scope)))
    else:
      location = ast.ExprSingle(ast.ElemNumber(
          tab.lookup_master_location(chan.name, elem.index, scope)))
    chanend = ast.ElemId(chan.chanend)
    chanend.symbol = Symbol(chan.chanend, self.chanend_type(chan), 
        None, scope=T_SCOPE_PROC)
    chanid = ast.ExprSingle(ast.ElemNumber(connid))
    return ast.StmtConnect(chanend, chanid, location, 
        self.connect_type(chan, master))

  def gen_array_conn(self, tab, scope, chan):
    """
    Generate a conncection for an array channel declaration. We must analyse
    the subscript by generating nested conditional statements. 'chan' is a
    ChanElemSet with multiple elements.
    """
    
    def create_single_connection(s, chan, indicies_expr, 
        range_begin, index, master, connid):
      debug(self.debug, 'New connection for index {}'.format(index))
      if master:
        location = ast.ExprSingle(ast.ElemNumber(
            tab.lookup_slave_location(chan.name, index, scope)))
      else:
        location = ast.ExprSingle(ast.ElemNumber(
            tab.lookup_master_location(chan.name, index, scope)))
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
      debug(self.debug, 'New connection over range {} to {}'.format(begin, end))
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
        return tab.lookup_slave_location(name, index, scope)
      else:
        return tab.lookup_master_location(name, index, scope)

    # Sort the channel elements into increasing order of indicies
    chan.elems = sorted(chan.elems, key=lambda x: x.indicies_value)

    # Build a list of channel index ranges
    debug(self.debug, '=====')
    x = chan.elems[0] 
    l = [[x, x]]
    master = tab.lookup_is_master(chan.name, x.index, x.location, scope)
    diff = target_loc(chan.name, x.index, master) - x.indicies_value
    debug(self.debug, '{}: -> {}[{}]: target {} diff {}'.format(x.indicies_value, 
        chan.name, x.index, target_loc(chan.name, x.index, master), diff))
    for x in chan.elems[1:]:
      cmaster = tab.lookup_is_master(chan.name, x.index, x.location, scope)
      cdiff = target_loc(chan.name, x.index, cmaster) - x.indicies_value
      debug(self.debug, '{}: {}[{}] -> target {} diff {}'.format(x.indicies_value, 
          chan.name, x.index, target_loc(chan.name, x.index, cmaster), cdiff))
      if diff == cdiff and master == cmaster:
        l[-1][1] = x
      else:
        diff = cdiff
        master = cmaster
        l.append([x, x])
  
    # Print them
    if self.debug:
      for x in l:
        print('Range: {}'.format(' '.join(['{}'.format(y.index) for y in x])))

    # Construct the connection syntax
    s = None
    i_expr = indicies_expr(chan.indicies)
    for x in reversed(l):
      master = tab.lookup_is_master(chan.name, x[0].index, x[0].location, scope)
      connid = tab.lookup(chan.name, x[0].index, scope).connid
      if x[0] == x[1]:
        s = create_single_connection(s, chan, i_expr, x[0].indicies_value, 
            x[0].index, master, connid)
      else:
        diff = (target_loc(chan.name, x[0].index, master) -
            x[0].indicies_value)
        s = create_range_connection(s, chan, i_expr, x[0].indicies_value,
            x[1].indicies_value, master, diff, connid)

    return s

  def insert_connections(self, tab, scope, stmt, chans):
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
          conns.append(self.gen_single_conn(tab, scope, x))
        else:
          conns.append(self.gen_array_conn(tab, scope, x))
      if len(conns) > 1:
        s1 = ast.StmtPar([], conns) 
        s1.location = stmt.location
        s1.chans = []
        decls = self.create_decls(tab, scope, chans)
        s2 = ast.StmtSeq(decls, [s1, stmt])
        s2.location = stmt.location
        s2.chans = []
        return s2
      else:
        decls = self.create_decls(tab, scope, chans)
        s = ast.StmtSeq(decls, conns+[stmt])
        s.location = stmt.location
        s.chans = []
        return s
    else:
      return stmt

  def create_decls(self, tab, scope, chansets):
    """
    Given 'chansets' (a list of 'ChanElemSet's) convert them into
    chanend declarations.
    """
    decls = []
    for x in chansets:
      #if tab.lookup(x.name, None, base=scope, scoped=True) != None:
      if x.symbol.scope == T_SCOPE_PROC:
        d = ast.VarDecl(x.chanend, T_CHANEND_SINGLE, None)
        d.symbol = Symbol(x.chanend, T_CHANEND_SINGLE, None, scope=T_SCOPE_PROC)
        decls.append(d)
      
      elif x.symbol.scope == T_SCOPE_BLOCK:
        d = ast.VarDecl(x.chanend, T_CHANEND_SINGLE, None)
        d.symbol = Symbol(x.chanend, T_CHANEND_SINGLE, None, scope=T_SCOPE_BLOCK)
        decls.append(d)
      
      elif x.symbol.scope == T_SCOPE_SERVER:
        d = ast.VarDecl(x.chanend, T_CHANEND_SERVER_SINGLE, None)
        d.symbol = Symbol(x.chanend, T_CHANEND_SERVER_SINGLE, None,
            scope=T_SCOPE_SERVER)
        decls.append(d)
      
      elif x.symbol.scope == T_SCOPE_CLIENT:
        d = ast.VarDecl(x.chanend, T_CHANEND_CLIENT_SINGLE, None)
        d.symbol = Symbol(x.chanend, T_CHANEND_CLIENT_SINGLE, None,
            scope=T_SCOPE_CLIENT)
        decls.append(d)
      
      else:
        assert 0
    return decls

  def display_chans(self, chans):
    if self.debug:
      pass

  # Program ============================================

  def walk_program(self, node):
    [self.defn(x) for x in node.defs]
  
  # Procedure definitions ===============================

  def defn(self, node):
    debug(self.debug, 'Inserting connections for: '+node.name)
    self.stmt(node.stmt, node.chantab, None)
    debug(self.debug, '[def connections]:')
    self.display_chans(node.chans)
  
  # Statements ==========================================

  # Top-level statements where connections are inserted

  # New scope
  def stmt_par(self, node, tab, scope):
    chansets = []
    debug(self.debug, '[par connections]:')
    for (i, (x, y)) in enumerate(zip(node.stmt, node.chans)):
      debug(self.debug, '[process {}]: '.format(i))
      chansets += self.stmt(x, tab, node.scope)
      node.stmt[i] = self.insert_connections(tab, node.scope, node.stmt[i], y)
      self.display_chans(y)
    [chansets.extend(x) for x in node.chans]
    #node.decls += self.take_decls(tab, node.scope, chansets)
    return chansets

  # New scope
  def stmt_server(self, node, tab, scope):
    chansets = []
    debug(self.debug, '[server connections]:')
    chansets += self.stmt(node.server, tab, node.scope)
    node.server = self.insert_connections(tab, node.scope, node.server, node.chans[0])
    self.display_chans(node.chans[0])
    debug(self.debug, '[client connections]:')
    chansets += self.stmt(node.client, tab, node.scope)
    node.client = self.insert_connections(tab, node.scope, node.client, node.chans[1])
    self.display_chans(node.chans[1])
    [chansets.extend(x) for x in node.chans]
    #node.decls += self.take_decls(tab, node.scope, chansets)
    return chansets

  def stmt_rep(self, node, tab, scope):
    debug(self.debug, '[rep connections]:')
    self.display_chans(node.chans)
    chansets = self.stmt(node.stmt, tab, scope)
    node.stmt = self.insert_connections(tab, scope, node.stmt, node.chans)
    #node.stmt.stmt.decls += self.take_decls(tab, scope, chansets+node.chans)
    return chansets + node.chans

  def stmt_on(self, node, tab, scope):
    debug(self.debug, '[on connections]:')
    self.display_chans(node.chans)
    chansets = self.stmt(node.stmt, tab, scope)
    node.stmt = self.insert_connections(tab, scope, node.stmt, node.chans)
    #node.stmt.stmt.decls += self.take_decls(tab, scope, chansets+node.chans)
    return chansets + node.chans

  # Other statements containing processes

  # New scope
  def stmt_seq(self, node, tab, scope):
    chansets = []
    [chansets.extend(self.stmt(x, tab, node.scope)) for x in node.stmt]
    #node.decls += self.take_decls(tab, node.scope, chansets)
    return chansets

  def stmt_if(self, node, tab, scope):
    chansets = self.stmt(node.thenstmt, tab, scope)
    chansets += self.stmt(node.elsestmt, tab, scope)
    return chansets

  def stmt_while(self, node, tab, scope):
    return self.stmt(node.stmt, tab, scope)

  def stmt_for(self, node, tab, scope):
    return self.stmt(node.stmt, tab, scope)

  # Other statements

  def stmt_in(self, node, tab, scope):
    return []

  def stmt_out(self, node, tab, scope):
    return []

  def stmt_pcall(self, node, tab, scope):
    return []
    
  def stmt_ass(self, node, tab, scope):
    return []

  def stmt_alias(self, node, tab, scope):
    return []

  def stmt_skip(self, node, tab, scope):
    return []

  def stmt_connect(self, node, tab, scope):
    return []

  def stmt_assert(self, node, tab, scope):
    return []

  def stmt_return(self, node, tab, scope):
    return []

