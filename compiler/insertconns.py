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

  def gen_single_conn(self, tab, pid, chan):
    """
    Generate a connection for a single channel declaration. 'chan' is a
    ChanElemSet with one element.
    """
    elem = chan.elems[0]
    off = ast.ExprSingle(ast.ElemNumber(
        tab.lookup_slave_offset(chan.name, elem.index)))
    loc = form_location(self.sym, pid, off, 1) if elem.master else None
    chanend = ast.ElemId(chan.chanend)
    chanend.symbol = Symbol(chan.chanend, T_CHANEND_SINGLE, 
        None, scope=T_SCOPE_PROC)
    chanid = ast.ExprSingle(ast.ElemNumber(
        tab.lookup_id(chan.name, elem.index)))
    return ast.StmtConnect(chanend, chanid, loc)

  def gen_array_conn(self, tab, pid, chan):
    """
    Generate a conncection for an array channel declaration. We must analyse
    the subscript by generating nested conditional statements. 'chan' is a
    ChanElemSet with multiple elements.
    """
    
    def create_single_connection(s, chan, index, master):
      print('New connection for index {}'.format(index))
      if master:
        offset_expr = ast.ExprSingle(ast.ElemNumber(
            tab.lookup_slave_offset(chan.name, index)))
        location = form_location(self.sym, pid, offset_expr, 1)
      else:
        location = None
      chanend = ast.ElemId(chan.chanend)
      chanend.symbol = Symbol(chan.chanend, T_CHANEND_SINGLE, None, scope=T_SCOPE_PROC)
      chanid = ast.ExprSingle(ast.ElemNumber(tab.lookup_id(chan.name, index)))
      cond = ast.ExprBinop('=', ast.ElemGroup(chan.expr), ast.ElemNumber(index))
      conn = ast.StmtConnect(chanend, chanid, location)
      return ast.StmtIf(cond, conn, s) if s else conn

    def create_range_connection(s, chan, r_begin, r_end, master, inclusive=False):
      print('New connection over range {} to {}'.format(r_begin, r_end))
      if master:
        offset_expr = ast.ExprSingle(ast.ElemNumber(math.floor(math.fabs(difference))))
        offset_expr = ast.ExprUnary('-', offset_expr) if difference<0 else offset_expr
        offset_expr = ast.ExprBinop('+', ast.ElemGroup(chan.expr), offset_expr)
        location = form_location(self.sym, pid, offset_expr, 1)
      else:
        location = None
      chanend = ast.ElemId(chan.chanend)
      chanend.symbol = Symbol(chan.chanend, T_CHANEND_SINGLE, None, scope=T_SCOPE_PROC)
      chanid = ast.ExprSingle(ast.ElemNumber(tab.lookup_id(chan.name, r_begin)))
      cond = ast.ExprBinop('and', 
          ast.ElemGroup(ast.ExprBinop('>=' if inclusive else '>', 
            ast.ElemGroup(chan.expr),
            ast.ExprSingle(ast.ElemNumber(min(r_begin, r_end))))),
          ast.ExprBinop('<=', ast.ElemGroup(chan.expr),
            ast.ExprSingle(ast.ElemNumber(max(r_begin, r_end)))))
      conn = ast.StmtConnect(chanend, chanid, location)
      return ast.StmtIf(cond, conn, s) if s else conn

    
    first = chan.elems[0]
    difference = (tab.lookup_slave_offset(chan.name, first.index) - index 
        if first.master else None)
    master = first.master
    begin = first.index
    end = None
  
    for (i, x) in enumerate(chan.elems):
      index = x.index
      offset = tab.lookup_slave_offset(chan.name, y.index) 
    
      if (master and offset-index == difference):
        print('  {} in master range'.format(index))
      elif (not master and not y.master):
        print('  {} in slave range'.format(index))

"""
    s = ast.StmtSkip()
    difference = None
    range_begin = None
    range_end = None
    looking = False
    master = False

    for (i, y) in enumerate(reversed(chan.elems)):
      index = y.index
      offset = tab.lookup_slave_offset(chan.name, y.index) 

      if not looking:
        range_begin = index
        looking = True
        difference = offset - index if y.master else None
        master = y.master
        print('Looking for new range from index {} with difference {}'
            .format(index, difference))
      else:

        # Inside a connection range
        if (master and offset - index == difference) or (not master and not y.master):
          print('Connection with index {} in range'.format(index))
          pass

        # End of a connection range
        else:
          print('End of range at index {}'.format(index))
          range_end = index
          if math.fabs(range_end-range_begin) < 1:
            s = create_single_connection(s, chan, range_begin, master)
          else:
            s = create_range_connection(s, chan, range_begin, range_end, master)

          # Start the new range
          range_begin = range_end
          difference = offset - index if y.master else None
          master = y.master
          print('Looking for new range from index {} with difference {}'
              .format(index, difference))

    # Close the last range (NOTE: we want to include the last index for ranges)
    range_end = chan.elems[0].index 
    if math.fabs(range_end-range_begin) <= 1:
      s = create_single_connection(s, chan, range_begin, master)
    else:
      s = create_range_connection(s, chan, range_begin, range_end, master,
          inclusive=True)

    print('====')
"""
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
      pid = ast.ElemId(PROC_ID_VAR)
      pid.symbol = Symbol(pid.name, T_VAR_SINGLE, scope=T_SCOPE_PROC)
      conns = []
      for x in chans:
        if len(x.elems) == 1:
          conns.append(self.gen_single_conn(tab, pid, x))
        else:
          conns.append(self.gen_array_conn(tab, pid, x))

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
      self.display_chans(node.chans)
  
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

  def stmt_on(self, node, tab, decls):
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

  def stmt_connect(self, node, tab, decls):
    pass

