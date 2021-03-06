# Copyright (c) 2011, James Hanlon, All rights reserved
# This software is freely distributable under a derivative of the
# University of Illinois/NCSA Open Source License posted in
# LICENSE.txt and at <http://github.xcore.com/>

from walker import NodeWalker
from typedefs import *

class LabelConns(NodeWalker):
  """
  Label connections with identifers by performing a greedy colouring of
  ChanElemSets.

  TODO: Recognise tree-connection patterns and ensure the assignment of
  connection IDs is compatible with the compression scheme.
  """
  def __init__(self):
    self.connid_count = 0

  def fill(self, tab, scope, chanset, connid):
    # Assign connid to all elements of the ChanElemSet
    [tab.set_connid(chanset.name, y.index, scope, connid) for y in chanset.elems]

  def assign(self, tab, scope, chans):
    for x in chans:
      if x.symbol.type == T_CHAN_SINGLE or \
          x.symbol.type == T_CHAN_ARRAY:
        x.connid = self.connid_count
        self.connid_count += 1
        for y in x.elems:
          chan_item = tab.lookup(x.name, y.index, scope)
          if chan_item.connid != x.connid:
            chanset = tab.lookup_chanset(x, y, scope)
            self.fill(tab, scope, chanset, x.connid)

  # Program ============================================

  def walk_program(self, node):
    [self.defn(x) for x in node.defs]
  
  def defn(self, node):
    self.assign(node.chantab, None, node.chans)
    self.stmt(node.stmt, node.chantab, None)
  
  # Statements ==========================================

  # Statements with lists of ChanElemSets

  # New scope
  def stmt_par(self, node, tab, scope):
    [self.assign(tab, node.scope, x) for x in node.chans]
    [self.stmt(x, tab, node.scope) for x in node.stmt]

  # New scope
  def stmt_server(self, node, tab, scope):
    [self.assign(tab, node.scope, x) for x in node.chans]
    self.stmt(node.server, tab, node.scope)
    self.stmt(node.client, tab, node.scope)

  def stmt_rep(self, node, tab, scope):
    self.assign(tab, scope, node.chans)
    self.stmt(node.stmt, tab, scope)
    
  def stmt_on(self, node, tab, scope):
    self.assign(tab, scope, node.chans)
    self.stmt(node.stmt, tab, scope)

  # Statements without

  # New scope
  def stmt_seq(self, node, tab, scope):
    [self.stmt(x, tab, node.scope) for x in node.stmt]

  def stmt_if(self, node, tab, scope):
    self.stmt(node.thenstmt, tab, scope)
    self.stmt(node.elsestmt, tab, scope)

  def stmt_while(self, node, tab, scope):
    self.stmt(node.stmt, tab, scope)

  def stmt_for(self, node, tab, scope):
    self.stmt(node.stmt, tab, scope)

  def stmt_skip(self, node, tab, scope):
    pass

  def stmt_pcall(self, node, tab, scope):
    pass

  def stmt_ass(self, node, tab, scope):
    pass

  def stmt_in(self, node, tab, scope):
    pass

  def stmt_out(self, node, tab, scope):
    pass

  def stmt_in_tag(self, node, tab, scope):
    pass

  def stmt_out_tag(self, node, tab, scope):
    pass

  def stmt_alias(self, node, tab, scope):
    pass

  def stmt_connect(self, node, tab, scope):
    pass

  def stmt_assert(self, node, tab, scope):
    pass

  def stmt_return(self, node, tab, scope):
    pass

