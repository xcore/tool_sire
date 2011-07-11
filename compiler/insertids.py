# Copyright (c) 2011, James Hanlon, All rights reserved
# This software is freely distributable under a derivative of the
# University of Illinois/NCSA Open Source License posted in
# LICENSE.txt and at <http://github.xcore.com/>

from walker import NodeWalker
from definitions import PROC_ID_VAR
from typedefs import T_VAR_SINGLE, T_SCOPE_PROC
from symbol import Symbol
import ast

class InsertIds(NodeWalker):
  """
  Insert assignment of procid() builtin to procedures containing a replicator.
  """
  def __init__(self):
    pass

  # Program ============================================

  def walk_program(self, node):
    [self.defn(x) for x in node.defs]
  
  # Procedure definitions ===============================

  def defn(self, node):
    if self.stmt(node.stmt):

      # Add a declaration for the variable
      node.decls.append(ast.Decl(PROC_ID_VAR, T_VAR_SINGLE, None))

      # Create the assignment
      e = ast.ElemId(PROC_ID_VAR)
      e.symbol = Symbol(PROC_ID_VAR, T_VAR_SINGLE, None, T_SCOPE_PROC)
      s = ast.StmtAss(e, ast.ExprSingle(ast.ElemFcall('procid', [])))

      # Add the assignent in sequence with the existing body process
      if isinstance(node.stmt, ast.StmtSeq):
        node.stmt.stmt.insert(0, s)
      else:
        node.stmt = ast.StmtSeq([s, node.stmt])
  
  # Statements ==========================================

  def stmt_rep(self, node):
    return True
    
  def stmt_seq(self, node):
    return any([self.stmt(x) for x in node.stmt])

  def stmt_par(self, node):
    return any([self.stmt(x) for x in node.stmt])

  def stmt_if(self, node):
    return self.stmt(node.thenstmt) or self.stmt(node.elsestmt)

  def stmt_while(self, node):
    return self.stmt(node.stmt)

  def stmt_for(self, node):
    return self.stmt(node.stmt)

  def stmt_on(self, node):
    return self.stmt(node.stmt)

  def stmt_return(self, node):
    return False
  
  def stmt_skip(self, node):
    return False

  def stmt_pcall(self, node):
    return False

  def stmt_ass(self, node):
    return False

  def stmt_in(self, node):
    return False

  def stmt_out(self, node):
    return False

  def stmt_alias(self, node):
    return False

  def stmt_connect(self, node):
    return False

