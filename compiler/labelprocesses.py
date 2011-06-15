# Copyright (c) 2011, James Hanlon, All rights reserved
# This software is freely distributable under a derivative of the
# University of Illinois/NCSA Open Source License posted in
# LICENSE.txt and at <http://github.xcore.com/>

from walker import NodeWalker

class TemplateWalker(NodeWalker):
  """
  A template recursive descent AST NodeWalker.
  """
  def __init__(self):
    pass

  # Program ============================================

  def walk_program(self, node):
    [self.defn(x) for x in node.defs]
  
  # Procedure definitions ===============================

  def defn(self, node):
    if node.name == 'main':
      self.stmt(node.stmt, ast.ExprSingle(ast.ElemNumber(0)))
    else
      self.stmt(node.stmt, ast.ExprSingle(ast.ElemPcall('procid')))
  
  # Statements ==========================================

  # Contain processes with new locations

  def stmt_rep(self, node, l):
    self.location = l
    #[self.elem(x) for x in node.indicies]
    # Determine f and then set l = g(a, b, .., k, f)
    self.stmt(node.stmt)
    
  def stmt_on(self, node, l):
    self.location = l
    self.stmt(node.stmt, node.core.expr)

  # Contain local processes

  def stmt_seq(self, node, l):
    self.location = l
    [self.stmt(x, l) for x in node.stmt]

  def stmt_par(self, node):
    self.location = l
    [self.stmt(x, l) for x in node.stmt]

  def stmt_if(self, node, l):
    self.location = l
    self.stmt(node.thenstmt, l)
    self.stmt(node.elsestmt, l)

  def stmt_while(self, node):
    self.location = l
    self.stmt(node.stmt, l)

  def stmt_for(self, node):
    self.location = l
    self.stmt(node.stmt, l)

  # Statements
  
  def stmt_skip(self, node):
    self.location = l

  def stmt_pcall(self, node):
    self.location = l

  def stmt_ass(self, node):
    self.location = l

  def stmt_in(self, node):
    self.location = l

  def stmt_out(self, node):
    self.location = l

  def stmt_alias(self, node):
    self.location = l

  def stmt_connect(self, node):
    self.location = l

  def stmt_return(self, node):
    self.location = l

