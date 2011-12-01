# Copyright (c) 2011, James Hanlon, All rights reserved
# This software is freely distributable under a derivative of the
# University of Illinois/NCSA Open Source License posted in
# LICENSE.txt and at <http://github.xcore.com/>

import copy
from functools import reduce
from walker import NodeWalker
import ast
from rename import Rename
from subelem import SubElem
from typedefs import *

class ExpandProcs(NodeWalker):
  """
  Expand procedures by substibuting the defined process.
  """
  def __init__(self, sig, node):
    self.sig = sig
    self.ast = node
    self.subs = dict([(x.name, 0) for x in self.ast.defs])

  def substitute(self, stmt):
    """
    Given a procedure call statement, return the process body for the
    procedure.
    """
    if isinstance(stmt, ast.StmtPcall) and self.sig.is_mobile(stmt.name):
      defn = [x for x in self.ast.defs if x.name == stmt.name][0]
      proc = copy.deepcopy(defn.stmt)

       # Rename actual parameters for ocurrances of formals
      for (x, y) in zip(defn.formals, stmt.args):
        if x.type == T_VAL_SINGLE:
          proc.accept(SubElem(ast.ElemId(x.name), y))
        elif x.type == T_REF_SINGLE:
          proc.accept(SubElem(ast.ElemId(x.name), y.elem))
        elif x.type == T_REF_ARRAY:
          proc.accept(Rename(x.name, y.elem.name, y.elem.symbol))
        elif x.type == T_CHANEND_SINGLE:
          proc.accept(SubElem(ast.ElemId(x.name), y.elem))
        elif x.type == T_CHANEND_ARRAY:
          proc.accept(Rename(x.name, y.elem.name, y.elem.symbol))
        else:
          assert 0

      return proc
    else:
      return stmt

  # Program ============================================

  def walk_program(self, node):
    
    # Expand all procedure calls
    self.stmt(node.defs[-1].stmt)

    # Remove all (now redundant) procedure definitions
    [self.sig.remove(x.name) for x in node.defs[:-1] if x.type == T_PROC]
    node.defs = ([x for x in node.defs if x.type == T_FUNC] 
        + [node.defs[-1]])
  
  # Statements containing statements ====================
  
  def stmt_seq(self, node):
    for (i, x) in enumerate(node.stmt):
      node.stmt[i] = self.substitute(x)
      self.stmt(node.stmt[i])

  def stmt_par(self, node):
    for (i, x) in enumerate(node.stmt):
      node.stmt[i] = self.substitute(x)
      self.stmt(node.stmt[i])

  def stmt_server(self, node):
    node.server = self.substitute(node.server)
    node.client = self.substitute(node.client)
    self.stmt(node.server)
    self.stmt(node.client)

  def stmt_if(self, node):
    node.thenstmt = self.substitute(node.thenstmt)
    node.elsestmt = self.substitute(node.elsestmt)
    self.stmt(node.thenstmt)
    self.stmt(node.elsestmt)

  def stmt_while(self, node):
    node.stmt = self.substitute(node.stmt)
    self.stmt(node.stmt)

  def stmt_for(self, node):
    node.stmt = self.substitute(node.stmt)
    self.stmt(node.stmt)

  def stmt_rep(self, node):
    node.stmt = self.substitute(node.stmt)
    self.stmt(node.stmt)

  def stmt_on(self, node):
    node.stmt = self.substitute(node.stmt)
    self.stmt(node.stmt)

  # Statements ==========================================

  def stmt_pcall(self, node):
    pass

  def stmt_ass(self, node):
    pass

  def stmt_in(self, node):
    pass

  def stmt_out(self, node):
    pass

  def stmt_alias(self, node):
    pass

  def stmt_connect(self, node):
    pass

  def stmt_assert(self, node):
    pass

  def stmt_return(self, node):
    pass

  def stmt_skip(self, node):
    pass

