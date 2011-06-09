# Copyright (c) 2011, James Hanlon, All rights reserved
## This software is freely distributable under a derivative of the
## University of Illinois/NCSA Open Source License posted in
## LICENSE.txt and at <http://github.xcore.com/>

from ast import NodeVisitor

class Display(NodeVisitor):
  """ 
  An AST visitor class to display statements using a function f.
  """
  def __init__(self, f):
    self.f = f

  # Statements ==========================================

  def visit_stmt_seq(self, node):
    self.f(node)

  def visit_stmt_par(self, node):
    self.f(node)

  def visit_stmt_skip(self, node):
    self.f(node)

  def visit_stmt_pcall(self, node):
    self.f(node)

  def visit_stmt_ass(self, node):
    self.f(node)

  def visit_stmt_alias(self, node):
    self.f(node)

  def visit_stmt_if(self, node):
    self.f(node)

  def visit_stmt_while(self, node):
    self.f(node)

  def visit_stmt_for(self, node):
    self.f(node)

  def visit_stmt_rep(self, node):
    self.f(node)

  def visit_stmt_on(self, node):
    self.f(node)

  def visit_stmt_return(self, node):
    self.f(node)

