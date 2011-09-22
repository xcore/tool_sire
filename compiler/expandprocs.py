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
    Given a procedure call statement, return the process body for the procedure
    and a set of variabled declarations such that:
     - each variable declaration is renamed to make it unique
     - each ocurrance of a formal parameter is substituted by an expression if
       a value otherwise replaced by the new named actual.
    """
    if isinstance(stmt, ast.StmtPcall) and self.sig.is_mobile(stmt.name):
      defn = [x for x in self.ast.defs if x.name == stmt.name][0]
      proc = copy.deepcopy(defn.stmt)
      decls = []
      
      # Rename local declarations for inclusion in parent scope
      for x in defn.decls:
        name = '_'+defn.name+'{}'.format(self.subs[defn.name])+'_'+x.name
        proc.accept(Rename(x.name, name))
        decl = ast.Decl(name, x.type, x.expr)
        decl.symbol = x.symbol 
        decls.append(decl)

      # Rename actual parameters for ocurrances of formals
      for (x, y) in zip(defn.formals, stmt.args):
        if x.type == T_VAL_SINGLE:
          proc.accept(SubElem(ast.ElemId(x.name), ast.ElemGroup(y)))
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

      # Increment the substitution count
      self.subs[stmt.name] += 1

      return (decls, proc)
    else:
      return ([], stmt)

  # Program ============================================

  def walk_program(self, node):
    
    # Expand all procedure calls
    node.defs[-1].decls.extend(self.stmt(node.defs[-1].stmt))

    # Remove all (now redundant) procedure definitions
    [self.sig.remove(x.name) for x in node.defs[:-1] if x.type == T_PROC]
    node.defs = [x for x in node.defs if x.type == T_FUNC] + [node.defs[-1]]
  
  # Statements containing statements ====================
  
  def stmt_seq(self, node):
    decls = []
    for (i, x) in enumerate(node.stmt):
      (d, node.stmt[i]) = self.substitute(x)
      decls.extend(d)
      decls.extend(self.stmt(node.stmt[i]))
    return decls

  def stmt_par(self, node):
    decls = []
    for (i, x) in enumerate(node.stmt):
      (d, node.stmt[i]) = self.substitute(x)
      decls.extend(d)
      decls.extend(self.stmt(node.stmt[i]))
    return decls

  def stmt_server(self, node):
    (decls, node.server) = self.substitute(node.server)
    (d, node.client) = self.substitute(node.client)
    decls.extend(d)
    decls.extend(self.stmt(node.server))
    decls.extend(self.stmt(node.client))
    return decls

  def stmt_if(self, node):
    (decls, node.thenstmt) = self.substitute(node.thenstmt)
    (d, node.elsestmt) = self.substitute(node.elsestmt)
    decls.extend(d)
    decls.extend(self.stmt(node.thenstmt))
    decls.extend(self.stmt(node.elsestmt))
    return decls

  def stmt_while(self, node):
    (decls, node.stmt) = self.substitute(node.stmt)
    decls.extend(self.stmt(node.stmt))
    return decls

  def stmt_for(self, node):
    (decls, node.stmt) = self.substitute(node.stmt)
    decls.extend(self.stmt(node.stmt))
    return decls

  def stmt_rep(self, node):
    (decls, node.stmt) = self.substitute(node.stmt)
    decls.extend(self.stmt(node.stmt))
    return decls
    
  def stmt_on(self, node):
    (decls, node.stmt) = self.substitute(node.stmt)
    decls.extend(self.stmt(node.stmt))
    return decls

  # Statements ==========================================

  def stmt_pcall(self, node):
    return []

  def stmt_ass(self, node):
    return []

  def stmt_in(self, node):
    return []

  def stmt_out(self, node):
    return []

  def stmt_alias(self, node):
    return []

  def stmt_connect(self, node):
    return []

  def stmt_assert(self, node):
    return []

  def stmt_return(self, node):
    return []

  def stmt_skip(self, node):
    return []

