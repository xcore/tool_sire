# Copyright (c) 2011, James Hanlon, All rights reserved
# This software is freely distributable under a derivative of the
# University of Illinois/NCSA Open Source License posted in
# LICENSE.txt and at <http://github.xcore.com/>

from walker import NodeWalker

class LiveOut(NodeWalker):
  """
  Given a statement, return the set of live-out variables by traversing the
  tree and for each statement, determine if the sucesssive statement exits.
  """
  def __init__(self):
    pass

  def collect(self, stmt, succ):
    """
    Collect live-out variables from a statement if its successor is 'None',
    i.e. it exits the block we are analysing. For statements with multiple
    successors we only consider variables live on the non-backwards (forwards)
    branch. This only applies to for a while statements.
    """
    if succ == None:
      if len(stmt.succ) > 1:
        return stmt.out & stmt.succ[0].inp
      else:
        return stmt.out
    else:
      return set()

  def compute(self, node):
    return self.stmt(node, None)
  
  # Statements ==========================================

  # Compound statements

  def stmt_seq(self, node, succ):
    s = set()
    for (i, x) in enumerate(node.stmt):
      succ_ = node.stmt[i+1] if i<len(node.stmt)-1 else succ
      s |= self.stmt(x, succ_)
    return s

  def stmt_par(self, node, succ):
    s = set()
    for x in node.stmt:
      s |= self.stmt(x, succ)
    return s

  def stmt_server(self, node, succ):
    s = self.stmt(node.server, succ)
    return s | self.stmt(node.client, succ)

  def stmt_if(self, node, succ):
    s = self.stmt(node.thenstmt, succ)
    return s | self.stmt(node.elsestmt, succ)

  def stmt_while(self, node, succ):
    return self.stmt(node.stmt, succ)

  def stmt_for(self, node, succ):
    return self.stmt(node.stmt, succ)

  def stmt_rep(self, node, succ):
    return self.stmt(node.stmt, succ)
    
  def stmt_on(self, node, succ):
    return self.stmt(node.stmt, succ)

  # Simple statements

  def stmt_skip(self, node, succ):
    return self.collect(node, succ)

  def stmt_pcall(self, node, succ):
    return self.collect(node, succ)

  def stmt_ass(self, node, succ):
    return self.collect(node, succ)

  def stmt_in(self, node, succ):
    return self.collect(node, succ)

  def stmt_out(self, node, succ):
    return self.collect(node, succ)

  def stmt_in_tag(self, node, succ):
    return self.collect(node, succ)

  def stmt_out_tag(self, node, succ):
    return self.collect(node, succ)

  def stmt_alias(self, node, succ):
    return self.collect(node, succ)

  def stmt_connect(self, node, succ):
    return self.collect(node, succ)

  def stmt_assert(self, node, succ):
    return self.collect(node, succ)

  def stmt_return(self, node, succ):
    return self.collect(node, succ)

