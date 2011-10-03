# Copyright (c) 2011, James Hanlon, All rights reserved
# This software is freely distributable under a derivative of the
# University of Illinois/NCSA Open Source License posted in
# LICENSE.txt and at <http://github.xcore.com/>

from walker import NodeWalker

class LabelConns(NodeWalker):
  """
  Label connections with identifers by performing a greedy colouring of
  ChanElemSets.
  """
  def __init__(self):
    self.connid_count = 0

  def fill(self, tab, chanset, connid):
    # Assign connid to all elements of the ChanElemSet
    chanset.connid = connid
    for y in chanset.elems:
      chan_item = tab.lookup(chanset.name, y.index)
      chan_item.connid = connid

  def assign(self, tab, chans):
    for x in chans:
      x.connid = self.connid_count
      self.connid_count += 1
      for y in x.elems:
        chan_item = tab.lookup(x.name, y.index)
        if chan_item.connid != x.connid:
          master = tab.is_master(x.name, y.index, y.location)
          chanset = tab.lookup_chanset(x.name, y.index, master)
          self.fill(tab, chanset, x.connid)

  # Program ============================================

  def walk_program(self, node):
    [self.defn(x) for x in node.defs]
  
  def defn(self, node):
    self.assign(node.chantab, node.chans)
    self.stmt(node.stmt, node.chantab)
  
  # Statements ==========================================

  # Statements with ChanElemSets

  def stmt_par(self, node, tab):
    [self.assign(tab, x) for x in node.chans]
    [self.stmt(x, tab) for x in node.stmt]

  def stmt_server(self, node, tab):
    [self.assign(tab, x) for x in node.chans]
    self.stmt(node.server, tab)
    self.stmt(node.client, tab)

  def stmt_rep(self, node, tab):
    self.assign(tab, node.chans)
    self.stmt(node.stmt, tab)
    
  def stmt_on(self, node, tab):
    self.assign(tab, node.chans)
    self.stmt(node.stmt, tab)

  # Statements without

  def stmt_seq(self, node, tab):
    [self.stmt(x, tab) for x in node.stmt]

  def stmt_if(self, node, tab):
    self.stmt(node.thenstmt, tab)
    self.stmt(node.elsestmt, tab)

  def stmt_while(self, node, tab):
    self.stmt(node.stmt, tab)

  def stmt_for(self, node, tab):
    self.stmt(node.stmt, tab)

  def stmt_skip(self, node, tab):
    pass

  def stmt_pcall(self, node, tab):
    pass

  def stmt_ass(self, node, tab):
    pass

  def stmt_in(self, node, tab):
    pass

  def stmt_out(self, node, tab):
    pass

  def stmt_alias(self, node, tab):
    pass

  def stmt_connect(self, node, tab):
    pass

  def stmt_assert(self, node, tab):
    pass

  def stmt_return(self, node, tab):
    pass

