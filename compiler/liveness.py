# Copyright (c) 2011, James Hanlon, All rights reserved
# This software is freely distributable under a derivative of the
# University of Illinois/NCSA Open Source License posted in
# LICENSE.txt and at <http://github.xcore.com/>

import sys
import ast
from walker import NodeWalker
from display import Display

class Liveness(NodeWalker):
  """ 
  An AST walker class to perform liveness analysis. We perform a post-order
  traversal to perform a backwards analysis.
  """
  def __init__(self):
    pass

  def compute(self, stmt):
    """
    Compute the in and out sets for a stmt. Return true if there was a
    change in the in and out sets.
    """
    inp = stmt.inp.copy()
    out = stmt.out.copy()
    stmt.inp = stmt.use | (stmt.out - stmt.defs)
    stmt.out = set()
    [stmt.out.update(x.inp) for x in stmt.succ]
    return len(inp^stmt.inp)>0 or len(out^stmt.out)>0

  def print_livesets(self, stmt):
    print(stmt)
    print('Use: {}'.format(stmt.use))
    print('Def: {}'.format(stmt.defs))
    print('In:  {}'.format(stmt.inp))
    print('Out: {}'.format(stmt.out))
    print('')

  def run(self, node, debug=False):
    """
    Iteratively perform liveness analysis until there is no change in the in
    and out sets.
    """
    #node.accept(Display(self.print_livesets))
    
    while any([self.stmt(x.stmt) if x.stmt else False for x in node.defs]):
      if debug: 
        print('=========================================================')
        node.accept(Display(self.print_livesets))
        print('=========================================================')

    if debug:
      node.accept(Display(self.print_livesets))
  
  # Statements ==========================================

  def stmt_seq(self, node):
    a = any([self.stmt(x) for x in reversed(node.stmt)])
    b = self.compute(node)
    return a or b

  def stmt_par(self, node):
    a = any([self.stmt(x) for x in node.stmt])
    b = self.compute(node)
    return a or b

  def stmt_server(self, node):
    a = self.stmt(node.server)
    b = self.stmt(node.client)
    c = self.compute(node)
    return a or b or c

  def stmt_if(self, node):
    a = self.stmt(node.thenstmt)
    b = self.stmt(node.elsestmt)
    c = self.compute(node)
    return a or b or c

  def stmt_while(self, node):
    a = self.stmt(node.stmt)
    b = self.compute(node)
    return a or b

  def stmt_for(self, node):
    a = self.stmt(node.stmt)
    b = self.compute(node)
    return a or b

  def stmt_rep(self, node):
    b = self.stmt(node.stmt)
    a = self.compute(node)
    return a or b

  def stmt_on(self, node):
    b = self.stmt(node.stmt)
    a = self.compute(node)
    return a or b

  def stmt_skip(self, node):
    return self.compute(node)

  def stmt_pcall(self, node):
    return self.compute(node)

  def stmt_ass(self, node):
    return self.compute(node)

  def stmt_in(self, node):
    return self.compute(node)

  def stmt_out(self, node):
    return self.compute(node)

  def stmt_in_tag(self, node):
    return self.compute(node)

  def stmt_out_tag(self, node):
    return self.compute(node)

  def stmt_alias(self, node):
    return self.compute(node)

  def stmt_connect(self, node):
    return self.compute(node)

  def stmt_assert(self, node):
    return self.compute(node)

  def stmt_return(self, node):
    return self.compute(node)

