# Copyright (c) 2011, James Hanlon, All rights reserved
# This software is freely distributable under a derivative of the
# University of Illinois/NCSA Open Source License posted in
# LICENSE.txt and at <http://github.xcore.com/>

import copy
from functools import reduce
from walker import NodeWalker
import ast
from replacename import ReplaceName
from subname import SubName
from typedefs import *

class ExpandProcs(NodeWalker):
  """
  Expand procedures by substibuting the defined process.
  """
  def __init__(self, node, verbose=False):
    self.ast = node
    self.subs = dict([(x.name, 0) for x in self.ast.defs])
    self.verbose = verbose

  def substitute(self, stmt): 
    if isinstance(stmt, ast.StmtPcall):
      defn = [x for x in self.ast.defs if x.name == stmt.name][0]
      proc = copy.deepcopy(defn.stmt)
      decls = []
      
      # Rename local declarations for inclusion in parent scope
      for x in defn.decls:
        name = '_'+defn.name+'_'+x.name+''+'{}'.format(self.subs[defn.name])
        proc.accept(ReplaceName(x.name, name))
        decls.append(ast.Decl(name, x.type, x.expr))

      # Rename actual parameters for ocurrances of formals
      for (x, y) in zip(defn.formals, stmt.args):
        if x.type == T_VAL_SINGLE:
          proc.accept(SubName(x.name, y))
        else:
          proc.accept(ReplaceName(x.name, y.elem.name))

      # Increment the substitution count
      self.subs[stmt.name] += 1

      return (decls, proc)
    else:
      return ([], stmt)

  # Program ============================================

  def walk_program(self, node):
    node.defs[-1].decls.extend(self.stmt(node.defs[-1].stmt))
  
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
    (d, node.slave) = self.substitute(node.slave)
    decls.extend(d)
    decls.extend(self.stmt(node.server))
    decls.extend(self.stmt(node.slave))
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

