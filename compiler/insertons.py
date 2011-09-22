# Copyright (c) 2011, James Hanlon, All rights reserved
# This software is freely distributable under a derivative of the
# University of Illinois/NCSA Open Source License posted in
# LICENSE.txt and at <http://github.xcore.com/>

from functools import reduce

from util import vmsg
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

  def walk_program(self, node, v):
  
    if not self.disable:
      
      # All processes have been flattened into 'main'
      self.defs = node.defs
      d = self.stmt(node.defs[-1].stmt, node.defs[-1].name, 0)
      
      # Check the available number of processors has not been exceeded
      if d > self.device.num_cores():
        self.errorlog.report_error(
        'insufficient processors: {} required, {} available'
            .format(d, self.device.num_cores()))

      # Report processor usage
      vmsg(v, '  {}/{} processors used'.format(d, self.device.num_cores()))

  # Statements ==========================================

  # Main is flattened so this won't be called
  def stmt_pcall(self, node, parent, d):
    return 1

  # Statements containing statements

  def stmt_par(self, node, parent, d):
    """
    For processes in parallel composition, add 'on' prefixes to provide simple
    compile-time distribution. If any process is already prefixed with an 'on',
    then do not add any (this is mainly for the test cases).
    """
    if any([isinstance(x, ast.StmtOn) for x in node.stmt]):
      self.errorlog.report_error("parallel composition contains 'on's")
      return 0
    e = self.stmt(node.stmt[0], parent, d)
    #print('par before d = {}'.format(e))
    for (i, x) in enumerate(node.stmt[1:]):
      node.stmt[i+1] = ast.StmtOn(ast.ExprSingle(ast.ElemNumber(d+e)), x)
      e += self.stmt(x, parent, d+e)
    #print('par after d = {}'.format(e))
    return e

  def stmt_server(self, node, parent, d):
    #print('d before = {}'.format(d))
    d += self.stmt(node.server, parent, d)
    #print('d after = {}'.format(d))
    node.client = ast.StmtOn(ast.ExprSingle(ast.ElemNumber(d)), node.client)
    d += self.stmt(node.client, parent, d)
    return d

  def stmt_rep(self, node, parent, d):
    """
    For replicated parallel statements, compute the offset as the product of
    index count values.
    """
    offset = reduce(lambda x, y: x*y.count_value, node.indicies, 1)
    e = self.stmt(node.stmt, parent, d)
    d += e
    return e * offset
    
  def stmt_on(self, node, parent, d):
    #assert 0
    return self.stmt(node.stmt, parent, d)

  def stmt_seq(self, node, parent, d):
    return max([self.stmt(x, parent, d) for x in node.stmt])

  def stmt_if(self, node, parent, d):
    d = self.stmt(node.thenstmt, parent, d)
    d = max(d, self.stmt(node.elsestmt, parent, d))
    return d

  def stmt_while(self, node, parent, d):
    return self.stmt(node.stmt, parent, d)

  def stmt_for(self, node, parent, d):
    return self.stmt(node.stmt, parent, d)

  # Statements not containing statements

  def stmt_ass(self, node, parent, d):
    return 1

  def stmt_in(self, node, parent, d):
    return 1

  def stmt_out(self, node, parent, d):
    return 1

  def stmt_alias(self, node, parent, d):
    return 1

  def stmt_connect(self, node, parent, d):
    return 1

  def stmt_assert(self, node, parent, d):
    return 1
  
  def stmt_return(self, node, parent, d):
    return 1
  
  def stmt_skip(self, node, parent, d):
    return 1

