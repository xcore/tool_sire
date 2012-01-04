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
from indices import indices_value, indices_expr

COMPRESS = True
DEBUG_COMPRESSION = False

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
    master = tab.lookup_is_master(chan, elem, scope)
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
    connid = tab.lookup_connid(chan.name, elem.index, scope)
    chanid = ast.ExprSingle(ast.ElemNumber(connid))
    return ast.StmtConnect(chanend, chanid, location, 
        self.connect_type(chan, master))

  def gen_array_conn(self, tab, scope, chan):
    """
    Generate a conncection for an array channel declaration. We must analyse
    the subscript by generating nested conditional statements. 'chan' is a
    ChanElemSet with multiple elements.
    """
    
    def target_loc(chan, elem, scope):
      master = tab.lookup_is_master(chan, elem, scope)
      return (tab.lookup_slave_location(chan.name, elem.index, scope) if master else
          tab.lookup_master_location(chan.name, elem.index, scope))

    def create_single_conn(s, chan, scope, i_elem, elem):
      debug(self.debug, 'New connection for index {}'.format(elem.index))
      master = tab.lookup_is_master(chan, elem, scope)
      if master:
        location = ast.ExprSingle(ast.ElemNumber(
            tab.lookup_slave_location(chan.name, elem.index, scope)))
      else:
        location = ast.ExprSingle(ast.ElemNumber(
            tab.lookup_master_location(chan.name, elem.index, scope)))
      chanend = ast.ElemId(chan.chanend)
      chanend.symbol = Symbol(chan.chanend, self.chanend_type(chan), 
          None, scope=T_SCOPE_PROC)
      connid = tab.lookup_connid(chan.name, elem.index, scope)
      chanid = ast.ExprSingle(ast.ElemNumber(connid))
      cond = ast.ExprBinop('=', i_elem,
          ast.ExprSingle(ast.ElemNumber(elem.indices_value)))
      conn = ast.StmtConnect(chanend, chanid, location, 
          self.connect_type(chan, master))
      return ast.StmtIf(cond, conn, s) if s!=None else conn

    def create_range_conn(s, chan, i_elem, group):
      diff2 = group[0]
      elem0 = group[1][0][0] 
      offset = target_loc(chan, elem0, scope)

      # Form the location expression
      if elem0.indices_value > 0:
        location = ast.ElemGroup(ast.ExprBinop('-', i_elem,
          ast.ExprSingle(ast.ElemNumber(elem0.indices_value))))
      else:
        location = i_elem
      location = ast.ExprBinop('*', ast.ElemNumber(diff2+1),
          ast.ExprSingle(location))
      location = ast.ExprBinop('+', ast.ElemGroup(location), 
          ast.ExprSingle(ast.ElemNumber(offset)))

      chanend = ast.ElemId(chan.chanend)
      chanend.symbol = Symbol(chan.chanend, self.chanend_type(chan), 
          None, scope=T_SCOPE_PROC)
      connid = tab.lookup_connid(chan.name, elem0.index, scope)
      chanid = ast.ExprSingle(ast.ElemNumber(connid))
      begin = elem0.indices_value
      end = group[1][-1][0].indices_value
      cond = ast.ExprBinop('>=', i_elem, 
          ast.ExprSingle(ast.ElemNumber(min(begin, end))))
      master = tab.lookup_is_master(chan, elem0, scope)
      conn = ast.StmtConnect(chanend, chanid, location,
          self.connect_type(chan, master))
      return ast.StmtIf(cond, conn, s) if s else conn

    def create_tree_conn(tab, scope, chan, phase, base_indices_value, 
        loc_base, loc_diff, connid_min, connid_offset, connid_diff, i_elem):
      location = ast.ExprBinop('-', i_elem,
          ast.ExprSingle(ast.ElemNumber(base_indices_value)))
      location = ast.ExprBinop('/', ast.ElemGroup(location),
          ast.ExprSingle(ast.ElemNumber(2)))
      location = ast.ExprBinop('*', ast.ElemNumber(loc_diff), 
          ast.ExprSingle(ast.ElemGroup(location)))
      location = ast.ExprBinop('+', ast.ElemNumber(loc_base),
          ast.ExprSingle(ast.ElemGroup(location)))
      chanend = ast.ElemId(chan.chanend)
      chanend.symbol = Symbol(chan.chanend, self.chanend_type(chan), 
          None, scope=T_SCOPE_PROC)
      elem0 = chan.elems[phase]
      connid = ast.ExprBinop('+', i_elem,
          ast.ExprSingle(ast.ElemNumber(connid_offset)))
      connid = ast.ExprBinop('rem', ast.ElemGroup(connid),
          ast.ExprSingle(ast.ElemNumber(2)))
      connid = ast.ExprBinop('*', ast.ElemGroup(connid),
          ast.ExprSingle(ast.ElemNumber(connid_diff)))
      connid = ast.ExprBinop('+', ast.ElemGroup(connid),
          ast.ExprSingle(ast.ElemNumber(connid_min)))
      master = tab.lookup_is_master(chan, elem0, scope)
      return ast.StmtConnect(chanend, connid, location,
          self.connect_type(chan, master))

    def conn_diff_groups(chan, s, i_elem, d=DEBUG_COMPRESSION):
      """
      Compress connecitons based on the difference between differences of
      indices value and destination.
      """
      # Build a list of channel elements and index-dest differences
      diffs = []
      for x in chan.elems:
        diff = target_loc(chan, x, scope) - x.indices_value
        diffs.append((x, diff))

      debug(d, 'Differences for chan {}:'.format(chan.name))
      for (elem, diff) in diffs:
        connid = tab.lookup_connid(chan.name, elem.index, scope)
        debug(d, '  {:>3}: [{}]:{} - {}'.format(elem.indices_value, elem.index,
          connid, diff))

      # Group consecutive elements with a constant second difference
      groups = []
      newgroup = True
      for ((elemA, diffA), (elemB, diffB)) in zip(diffs[:-1], diffs[1:]):
        diff2 = diffB - diffA
        connid = tab.lookup_connid(chan.name, elemB.index, scope)
        master = tab.lookup_is_master(chan, elemB, scope)
        if newgroup:
          groups.append((diff2, [(elemA, diffA)]))
          groupdiff2 = diff2
          groupconnid = tab.lookup_connid(chan.name, elemA.index, scope)
          groupmaster = tab.lookup_is_master(chan, elemA, scope)
          newgroup = False
        if (groupdiff2 == diff2 
            and groupconnid == connid
            and groupmaster == master):
          groups[-1][1].append((elemB, diffB))
        else:
          newgroup = True
      if newgroup:
        groups.append((None, [diffs[-1]]))
        
      debug(d, 'Groups:')
      for x in groups:
        diff2 = x[0]
        elem0 = x[1][0][0]
        offset = target_loc(chan, elem0, scope)
        debug(d, '  diff2:  {}'.format(diff2))
        debug(d, '  offset: {}'.format(offset))
        debug(d, '  base:   {}'.format(elem0.indices_value))
        if len(x[1]) > 1:
          for (i, (elem, diff)) in enumerate(x[1]):
            loc = target_loc(chan, elem, scope)
            computed = ((diff2+1) * (elem.indices_value-elem0.indices_value)) + offset
            assert computed == loc
            debug(d, '    {:>3}: [{:>3}]->{:>3}, diff: {:>3}, computed: {}'.format(
                elem.indices_value, elem.index, loc, diff, computed))
        else:
          debug(d, '    {:>3}: [{:>3}]->{:>3}'.format(
              elem0.indices_value, elem0.index, offset))

      # If compression was inneffective then abort
      if len(groups) == len(chan.elems):
        debug(d, 'Aborting group diff compression.')
        return None

      # Construct connection syntax
      s = None
      for x in groups:
        elem0 = x[1][0][0]
        if len(x[1]) == 1:
          s = create_single_conn(s, chan, scope, i_elem, elem0)
        else:
          s = create_range_conn(s, chan, i_elem, x)
      return s

    def conn_tree_groups(chan, s, i_elem, d=DEBUG_COMPRESSION):
      """
      Compress connections based on monotonically increasing or decreasing
      sets with the same target destination. Assume sets are of size 2.
      """
      locs = []
      debug(d, 'Locations:')
      for x in chan.elems:
        loc = target_loc(chan, x, scope)
        locs.append((x, loc))
        debug(d, '  {:>4} : {}[{}] -> {}'.format(x.indices_value, chan.name, x.index, loc))
       
      # Only consider more than three conditions 
      if len(locs) <= 3:
        debug(d, 'Aborting tree compression.')
        return None

      # Separate the first odd element if there is one
      phase = 0
      if locs[0][1] != locs[1][1]:
        odd_elem = locs[0][0]
        locs = locs[1:]
        phase = 1

      # Set parameters
      loc_diff = locs[2][1]-locs[1][1]
      loc_base = locs[0][1]
      base_indices_value = locs[0][0].indices_value
      connidA = tab.lookup_connid(chan.name, locs[0][0].index, scope)
      connidB = tab.lookup_connid(chan.name, locs[1][0].index, scope)
      connid_min = min(connidA, connidB)
      connid_diff = max(connidA, connidB) - connid_min
      connid_offset = (phase + (1 if connidA > connidB else 0)) % 2
      
      # Print some debug info
      debug(d, 'Attempting tree compression.')
      debug(d, '  Location base: {}'.format(loc_base))
      debug(d, '  Location diff: {}'.format(loc_diff))
      debug(d, '  Base ival:     {}'.format(base_indices_value))
      debug(d, '  ConnID base:   {}'.format(connidA))
      debug(d, '  ConnID diff:   {}'.format(connid_diff))

      # Check each pair
      end = 1+(math.floor((len(locs)-1)/2)*2)
      debug(d, 'Checking pairs 1 to {}'.format(end))
      for (x, y) in zip(locs[:-1:2], locs[1::2]):
        debug(d, '  {} and {}'.format(y[1], x[1]))
        if x[1] != y[1]:
          debug(d, 'Aborting tree compression.')
          return None
      
      # Check each step between pairs
      debug(d, 'Checking diffs 1 to {}'.format(end))
      for (x, y) in zip(locs[1::2], locs[2::2]):
        debug(d, '  {} and {}'.format(y[1], x[1]))
        connidX = tab.lookup_connid(chan.name, x[0].index, scope)
        connidY = tab.lookup_connid(chan.name, y[0].index, scope)
        connid_diff_ = connidX - connidY
        if y[1] - x[1] != loc_diff or connid_diff != connid_diff_:
          debug(d, 'Aborting tree compression.')
          return None

      # Check matching computed location
      debug(d, 'Matching form, checking computed:')
      if phase == 1:
        connid = tab.lookup_connid(chan.name, odd_elem.index, scope)
        debug(d, '  {}: connid={}'.format(odd_elem.indices_value, connid))
      for (elem, loc) in locs:
        computed_loc = loc_base + (loc_diff * (math.floor(
            ((elem.indices_value - base_indices_value))/2)))
        connid = tab.lookup_connid(chan.name, elem.index, scope)
        computed_connid = (connid_min + 
            ((elem.indices_value + connid_offset) % 2) * connid_diff)
        debug(d, '  {}: connid={}, loc={} computed({}, {})'
            .format(elem.indices_value, connid, loc, 
              computed_connid, computed_loc))
        assert computed_loc == loc
        assert computed_connid == connid

      # Construct connection syntax
      if phase == 0:
        return create_tree_conn(tab, scope, chan, phase, 
            base_indices_value, loc_base, loc_diff, 
            connid_min, connid_offset, connid_diff, i_elem)
      else:
        s = create_tree_conn(tab, scope, chan, phase, 
            base_indices_value, loc_base, loc_diff, 
            connid_min, connid_offset, connid_diff, i_elem)
        return create_single_conn(s, chan, scope, i_elem, 
            odd_elem.indices_value, odd_elem.index)

    def conn_singles(chan, s, i_elem, d=DEBUG_COMPRESSION):
      """
      Create (uncompressed) connections for each case.
      """
      debug(d, 'Creating uncompressed connection range.')
      for x in chan.elems:
        s = create_single_conn(s, chan, scope, i_elem, x)
        debug(d, '  {}: {}[{}]'.format(x.indices_value, chan.name, x.index))
      return s

    # Sort the channel elements into increasing order of indices
    chan.elems = sorted(chan.elems, key=lambda x: x.indices_value)

    # Compress conditional connections and return the AST construction
    i_expr = indices_expr(chan.indices)
    i_elem = ast.ElemId('_i')
    i_elem.symbol = Symbol(i_elem.name, T_VAR_SINGLE, scope=T_SCOPE_BLOCK)
    s = None
    if COMPRESS:
      s = conn_tree_groups(chan, s, i_elem)
      s = conn_diff_groups(chan, s, i_elem) if s==None else s 
    s = conn_singles(chan, s, i_elem) if s==None else s
    s = [ast.StmtAss(i_elem, i_expr), s]
    s = ast.StmtSeq([ast.VarDecl(i_elem.name, T_VAR_SINGLE, None)], s)
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

