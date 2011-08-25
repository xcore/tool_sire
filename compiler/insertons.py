# Copyright (c) 2011, James Hanlon, All rights reserved
# This software is freely distributable under a derivative of the
# University of Illinois/NCSA Open Source License posted in
# LICENSE.txt and at <http://github.xcore.com/>

from functools import reduce

from walker import NodeWalker
import ast

class InsertOns(NodeWalker):
  """
  Prefix processes with on in parallel composition to distribute them over a
  system. For example the process::
    
    { foo() || par i in [0 for N] do bar() || baz() }

  is translated as::

    { foo() || on 1 do par i in [0 for N] do bar() || on N+1 do baz() }
  """
  def __init__(self, device, errorlog, disable):
    self.device = device
    self.errorlog = errorlog
    self.disable = disable
    self.defs = None

  # Program ============================================

  def walk_program(self, node):
    #d = 0
    #for x in node.defs[:-1]:
    #  d = self.stmt(x.stmt, d)
    #  self.tab[x.name] = d
  
    # Start distribution from 'main'
    self.defs = node.defs
    d = self.stmt(node.defs[-1].stmt, 0)
    if d > self.device.num_cores():
      self.errorlog.report_error('insufficient processors: {} > {}'
          .format(d, self.device.num_cores()))

  # Statements ==========================================

  # We want to walk over the program by following process calls.

  def stmt_pcall(self, node, d):
    for x in self.defs:
      if x.name == node.name:
        return self.stmt(x.stmt, d)
    assert 0

  # Statements containing statements

  def stmt_par(self, node, d):
    """
    For processes in parallel composition, add 'on' prefixes to provide simple
    compile-time distribution. If any process is already prefixed with an 'on',
    then do not add any (this is mainly for the test cases).
    """
    if not self.disable:
      if any([isinstance(x, ast.StmtOn) for x in node.stmt]):
        self.errorlog.report_error("parallel composition contains 'on's")
        return 0
      d += self.stmt(node.stmt[0], d)
      for (i, x) in enumerate(node.stmt[1:]):
        node.stmt[i+1] = ast.StmtOn(ast.ExprSingle(ast.ElemNumber(d)), x)
        d += self.stmt(x, d)
      return d
    else:
      return max([self.stmt(x) for x in node.stmt])

  def stmt_rep(self, node, d):
    """
    For replicated parallel statements, compute the offset as the product of
    index count values.
    """
    offset = reduce(lambda x, y: x*y.count_value, node.indicies, 1)
    e = self.stmt(node.stmt, d)
    d += e
    return e * offset
    
  def stmt_seq(self, node, d):
    return max([self.stmt(x, d) for x in node.stmt])

  def stmt_on(self, node, d):
    return self.stmt(node.stmt, d)

  def stmt_if(self, node, d):
    d = self.stmt(node.thenstmt, d)
    d = max(d, self.stmt(node.elsestmt, d))
    return d

  def stmt_while(self, node, d):
    return self.stmt(node.stmt, d)

  def stmt_for(self, node, d):
    return self.stmt(node.stmt, d)

  # Statements not containing statements

  def stmt_ass(self, node, d):
    return 1

  def stmt_in(self, node, d):
    return 1

  def stmt_out(self, node, d):
    return 1

  def stmt_alias(self, node, d):
    return 1

  def stmt_connect(self, node, d):
    return 1

  def stmt_assert(self, node, d):
    return 1
  
  def stmt_return(self, node, d):
    return 1
  
  def stmt_skip(self, node, d):
    return 1

