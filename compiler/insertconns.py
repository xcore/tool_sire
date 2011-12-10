# Copyright (c) 2011, James Hanlon, All rights reserved
# This software is freely distributable under a derivative of the
# University of Illinois/NCSA Open Source License posted in
# LICENSE.txt and at <http://github.xcore.com/>

import math
import sys

import ast
from util import debug
from walker import NodeWalker
from definitions import *
from typedefs import *
from symboltab import Symbol
from formlocation import form_location
from printer import Printer
from indicies import indicies_value, indicies_expr

COMPRESS = True

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
    master = tab.lookup_is_master(chan.name, elem.index, chan.chanend, scope)
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
    
    def create_single_conn(s, chan, scope, indicies_expr, range_begin, index):
      debug(self.debug, 'New connection for index {}'.format(index))
      master = tab.lookup_is_master(chan.name, index, chan.chanend, scope)
      if master:
        location = ast.ExprSingle(ast.ElemNumber(
            tab.lookup_slave_location(chan.name, index, scope)))
      else:
        location = ast.ExprSingle(ast.ElemNumber(
            tab.lookup_master_location(chan.name, index, scope)))
      chanend = ast.ElemId(chan.chanend)
      chanend.symbol = Symbol(chan.chanend, self.chanend_type(chan), 
          None, scope=T_SCOPE_PROC)
      connid = tab.lookup(chan.name, index, scope).connid
      chanid = ast.ExprSingle(ast.ElemNumber(connid))
      cond = ast.ExprBinop('=', ast.ElemGroup(indicies_expr), 
          ast.ElemNumber(range_begin))
      conn = ast.StmtConnect(chanend, chanid, location, 
          self.connect_type(chan, master))
      return ast.StmtIf(cond, conn, s) if s else conn

    #def create_range_connection(s, chan, indicies_expr, begin, end, master,
    #    diff, connid):
    #  debug(self.debug, 'New connection over range {} to {}'.format(begin, end))
    #  if diff != 0:
    #    location = ast.ExprSingle(ast.ElemNumber(math.floor(math.fabs(diff))))
    #    location = ast.ExprUnary('-', location) if diff<0 else location
    #    location = ast.ExprBinop('+', ast.ElemGroup(indicies_expr), location)
    #  else:
    #    location = indicies_expr
    #  chanend = ast.ElemId(chan.chanend)
    #  chanend.symbol = Symbol(chan.chanend, self.chanend_type(chan), 
    #      None, scope=T_SCOPE_PROC)
    #  chanid = ast.ExprSingle(ast.ElemNumber(connid))
    #  cond = ast.ExprBinop('and', 
    #      ast.ElemGroup(ast.ExprBinop('>=', ast.ElemGroup(indicies_expr),
    #        ast.ExprSingle(ast.ElemNumber(min(begin, end))))),
    #      ast.ExprBinop('<=', ast.ElemGroup(indicies_expr),
    #        ast.ExprSingle(ast.ElemNumber(max(begin, end)))))
    #  conn = ast.StmtConnect(chanend, chanid, location,
    #      self.connect_type(chan, master))
    #  return ast.StmtIf(cond, conn, s) if s else conn

    def create_range_conn(s, chan, indicies_expr, group):
      # TODO: do single values of master and connid apply to whole range?
      diff2 = group[0]
      elem0 = group[1][0][0] 
      offset = target_loc(chan.name, elem0.index, chan.chanend, scope)
      location = ast.ExprBinop('-', ast.ElemGroup(indicies_expr),
          ast.ElemNumber(elem0.indicies_value))
      location = ast.ExprBinop('*', ast.ElemNumber(diff2+1),
          ast.ElemGroup(location))
      location = ast.ExprBinop('+', ast.ElemGroup(location), ast.ElemNumber(offset))
      chanend = ast.ElemId(chan.chanend)
      chanend.symbol = Symbol(chan.chanend, self.chanend_type(chan), 
          None, scope=T_SCOPE_PROC)
      connid = tab.lookup(chan.name, elem0.index, scope).connid
      chanid = ast.ExprSingle(ast.ElemNumber(connid))
      begin = elem0.index
      end = group[1][-1][0].index
      cond = ast.ExprBinop('and', 
          ast.ElemGroup(ast.ExprBinop('>=', ast.ElemGroup(indicies_expr),
            ast.ExprSingle(ast.ElemNumber(min(begin, end))))),
          ast.ExprBinop('<=', ast.ElemGroup(indicies_expr),
            ast.ExprSingle(ast.ElemNumber(max(begin, end)))))
      master = tab.lookup_is_master(chan.name, elem0.index, chan.chanend, scope)
      conn = ast.StmtConnect(chanend, chanid, location,
          self.connect_type(chan, master))
      return ast.StmtIf(cond, conn, s) if s else conn

    def target_loc(name, index, chanend, scope):
      master = tab.lookup_is_master(name, index, chanend, scope)
      return (tab.lookup_slave_location(name, index, scope) if master else
          tab.lookup_master_location(name, index, scope))

    # Sort the channel elements into increasing order of indicies
    chan.elems = sorted(chan.elems, key=lambda x: x.indicies_value)

    # Build a list of channel index ranges
    debug(self.debug, '=====')
    #x = chan.elems[0] 
    #l = [[x, x]]
    #master = tab.lookup_is_master(chan.name, x.index, chan.chanend, scope)
    #diff = target_loc(chan.name, x.index, master) - x.indicies_value
    #debug(self.debug, '{}: -> {}[{}]: target {} diff {}'.format(x.indicies_value, 
    #    chan.name, x.index, target_loc(chan.name, x.index, master), diff))
    #for x in chan.elems:
      #debug(self.debug, '{}: {}[{}] -> target {} diff {}'.format(x.indicies_value, 
      #    chan.name, x.index, target_loc(chan.name, x.index, cmaster), cdiff))
      #if diff == cdiff and master == cmaster:
      #  l[-1][1] = x
      #else:
      #diff = cdiff
      #master = cmaster
      #l.append([x, x])

    # Build a list of channel elements and index-dest differences
    diffs = []
    for x in chan.elems:
      diff = target_loc(chan.name, x.index, chan.chanend, scope) - x.indicies_value
      diffs.append((x, diff))

    print('Differences for chan {}:'.format(chan.name))
    for (elem, diff) in diffs:
      print('  {:>3}: [{}] : {}'.format(elem.indicies_value, elem.index, diff))

    # Group consecutive elements with a constant second difference
    # TODO: groups should share the same connection id
    groups = []
    if COMPRESS:
      newgroup = True
      skip = False
      for ((elemA, diffA), (elemB, diffB)) in zip(diffs[:-1], diffs[1:]):
        diff2 = diffB - diffA
        if skip:
          skip = False
          continue
        if newgroup:
          groups.append((diff2, [(elemA, diffA)]))
          groupdiff2 = diff2
          newgroup = False
        if groupdiff2 == diff2:
          groups[-1][1].append((elemB, diffB))
        else:
          newgroup = True
      if newgroup:
        groups.append((None, [diffs[-1]]))
    else:
      [groups.append((None, [x])) for x in diffs]
      
    # Print them
    #if self.debug:
    print('Groups:')
    for x in groups:
      diff2 = x[0]
      elem0 = x[1][0][0]
      offset = target_loc(chan.name, elem0.index, chan.chanend, scope)
      print('  diff2:  {}'.format(diff2))
      print('  offset: {}'.format(offset))
      print('  base:   {}'.format(elem0.indicies_value))
      if len(x[1]) > 1:
        for (i, (elem, diff)) in enumerate(x[1]):
          loc = target_loc(chan.name, elem.index, chan.chanend, scope)
          computed = ((diff2+1) * (elem.indicies_value-elem0.indicies_value)) + offset
          assert computed == loc
          print('    {:>3}: [{:>3}]->{:>3}, diff: {:>3}, computed: {}'.format(
              elem.indicies_value, elem.index, loc, diff, computed))
      else:
        print('    {:>3}: [{:>3}]->{:>3}'.format(
            elem0.indicies_value, elem0.index, offset))

    # Construct the connection syntax
    s = None
    i_expr = indicies_expr(chan.indicies)
    for x in groups:
      elem0 = x[1][0][0]
      if len(x[1]) == 1:
        s = create_single_conn(s, chan, scope, i_expr, 
            elem.indicies_value, elem0.index)
      else:
        s = create_range_conn(s, chan, i_expr, x)

    # Construct the connection syntax
    #l = []
    #for x in chan.elems:
    #  l.append([x, x])
    #s = None
    #i_expr = indicies_expr(chan.indicies)
    #for x in reversed(l):
    #  master = tab.lookup_is_master(chan.name, x[0].index, chan.chanend, scope)
    #  connid = tab.lookup(chan.name, x[0].index, scope).connid
    #  if x[0] == x[1]:
    #    s = create_single_connection(s, chan, i_expr, x[0].indicies_value, 
    #        x[0].index, master, connid)
    #  else:
    #    diff = (target_loc(chan.name, x[0].index, chan.chanend, scope) -
    #        x[0].indicies_value)
    #    s = create_range_connection(s, chan, i_expr, x[0].indicies_value,
    #        x[1].indicies_value, master, diff, connid)

    return s

  def insert_connections(self, tab, scope, stmt, chans):
    """
    Insert connections for a process from a list of channel uses (name, index)
    by composing them in sequence, prior to the process. If there are no
    connecitons to be made, just return the process.
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

