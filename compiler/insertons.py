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

  # Program ============================================

  def walk_program(self, node):
    for x in node.defs:
      d = self.stmt(x.stmt)
      if d > self.device.num_cores():
        self.errorlog.report_error('insufficient processors: {} > {}'
            .format(d, self.device.num_cores()))
  
  # Statements ==========================================

  # Statements containing statements

  def stmt_par(self, node):
    """
    For processes in parallel composition, add 'on' prefixes to provide simple
    compile-time distribution. If any process is already prefixed with an 'on',
    then do not add any (this is mainly for the test cases).
    """
    if any([isinstance(x, ast.StmtOn) for x in node.stmt]):
      self.errorlog.report_error("parallel composition contains 'on's")
      return d
    if not self.disable:
      d = self.stmt(node.stmt[0])
      for (i, x) in enumerate(node.stmt[1:]):
        node.stmt[i+1] = ast.StmtOn(ast.ExprSingle(ast.ElemNumber(d)), x)
        d += self.stmt(x)
      return d
    else:
      return max([self.stmt(x) for x in node.stmt])

  def stmt_rep(self, node):
    """
    For replicated parallel statements, compute the offset as the product of
    index count values.
    """
    offset = reduce(lambda x, y: x*y.count_value, node.indicies, 1)
    d = self.stmt(node.stmt)
    return d * offset
    
  def stmt_seq(self, node):
    return max([self.stmt(x) for x in node.stmt])

  def stmt_on(self, node):
    return self.stmt(node.stmt)

  def stmt_if(self, node):
    d = self.stmt(node.thenstmt)
    d = max(d, self.stmt(node.elsestmt))
    return d

  def stmt_while(self, node):
    return self.stmt(node.stmt)

  def stmt_for(self, node):
    return self.stmt(node.stmt)

  # Statements not containing statements

  def stmt_ass(self, node):
    return 1

  def stmt_in(self, node):
    return 1

  def stmt_out(self, node):
    return 1

  def stmt_alias(self, node):
    return 1

  def stmt_connect(self, node):
    return 1

  def stmt_assert(self, node):
    return 1
  
  def stmt_return(self, node):
    return 1
  
  def stmt_skip(self, node):
    return 1

  def stmt_pcall(self, node):
    return 1

