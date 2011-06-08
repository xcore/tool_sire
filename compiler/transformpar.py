# Copyright (c) 2011, James Hanlon, All rights reserved
# This software is freely distributable under a derivative of the
# University of Illinois/NCSA Open Source License posted in
# LICENSE.txt and at <http://github.xcore.com/>

import copy
import ast
from walker import NodeWalker
from freevars import FreeVars
from type import Type
from semantics import par_var_to_param
from semantics import rep_var_to_param

from printer import Printer

class TransformPar(NodeWalker):
  """
  An AST walker to transform parallel blocks. 
  
  From:
    proc p(...) is
      ...
      { stmt1 | stmt2 }
      ...

  To:
    proc _p1(live-in(stmt1)) is
      decls = {x|free-var(stmt1)-live-in(stmt1)}
      stmt1

    proc _p2(live-in(stmt2)) is
      decls = {x|free-var(stmt2)-live-in(stmt2)}
      stmt2

    proc p(...) is
      ...
      { _p1(live-in-actuals(stmt1)) | _p2(live-in-actuals(stmt2)) }
      ...

  Or from:
    par ... do stmt

  To:
    proc _p(live-in(stmt)) is
      decls = {x|free-var(stmt)-live-in(stmt)}
      stmt

    proc p(...) is
      ..
      par ... do _p(live-in-actuals(stmt))
      ..
  """
  def __init__(self, sem, sig, debug=False):
    self.sem = sem
    self.sig = sig
    self.debug = debug

  def stmt_to_process(self, stmt, indicies=[]):
    """
    Convert a statement into a process definition.
     - Create the definition node.
     - Create the corresponding Pcall node.
     - Insert the definition into the signature table.
     - Return the tuple (process-def, process-call)
    
    Also, the index varible (rep_var) of replicator statements must be
    treated as a value and not a variable in its use as a parameter
    (transform replicator stage) and passed-by-reference.
    """
    assert isinstance(stmt, ast.Stmt)
    # Sets for live-in and local decls (for non-live, non-array targets).
    live_in = stmt.inp.copy()
    local_decls = FreeVars().allvars(stmt) - live_in
    #Printer().stmt(stmt)

    # Create the formal and actual paramerer and local declaration lists
    formals = []
    actuals = []
    decls = []

    # Deal with the index variable of a replicator statement: add it as a
    # single value (not a variable) to the formals and as-is to the actuals, 
    # then remove it from the variable live-in set.
    for x in indicies:
      formals.append(ast.Param(x.name, Type('val', 'single'), None))
      actuals.append(ast.ExprSingle(ast.ElemId(x.name)))
      live_in -= set([x])

    # Replicated parallel statements are more restrivtive
    var_to_param = rep_var_to_param if len(indicies)>0 else par_var_to_param
    
    # For each variable in the live-in set add accordingly to formals and actuals.
    for x in live_in:

      # All parameters are added as formals with the appropriate conversion
      p = ast.Param(x.name, var_to_param[x.symbol.type], x.symbol.expr)
      p.symbol = x.symbol
      formals.append(p)

      # If the actual is an array subscript or slice, we only pass the id.
      if isinstance(x, ast.ElemSlice) or isinstance(x, ast.ElemSub):
        e = ast.ElemId(x.name)
        e.symbol = x.symbol
        actuals.append(ast.ExprSingle(e))
      else:
        actuals.append(ast.ExprSingle(copy.copy(x)))
    
      # For arrays with lengths specified with variables (i.e. arrays passed by
      # reference) then we must include the length as the next parameter.
      if (x.symbol.type.form == 'array' 
          and isinstance(x.symbol.expr, ast.ExprSingle)):
        p = ast.Param(x.symbol.expr.elem.name, Type('val', 'single'), None)
        formals.append(p)
        actuals.append(x.symbol.expr)
      
    # Create a unique name
    name = self.sig.unique_process_name()

    # Create the local declarations
    for x in local_decls:
      assert x.symbol.type == Type('var', 'single')
      decls.append(ast.Decl(x.name, Type('var', 'single'), None))
    
    # Create the new process definition
    d = ast.Def(name, Type('proc', 'procedure'), formals, decls, stmt)

    # perform semantic analysis to update symbol bindings. 
    #Printer().defn(d, 0)
    self.sem.defn(d)
    
    # Create the corresponding call.
    c = ast.StmtPcall(name, actuals)
    return (d, c)

  # Program ============================================

  def walk_program(self, node):
    """
    Build a new list of definitions with new process definitons occuring
    before their use. 
    """
    defs = []
    for x in node.defs:
      d = self.defn(x)
      if len(d)>0:
        defs.extend(reversed(d))
      defs.append(x)
    node.defs = defs
  
  # Procedure definitions ===============================

  def defn(self, node):
    return self.stmt(node.stmt) if node.stmt else []
  
  # Statements ==========================================

  def stmt_seq(self, node):
    p = []
    [p.extend(self.stmt(x)) for x in node.stmt]
    return p

  # Parallel composition
  def stmt_par(self, node):
    p = []
    [p.extend(self.stmt(x)) for x in node.stmt]
    for (i, x) in enumerate(node.stmt):
      if not isinstance(x, ast.StmtPcall):
        if(self.debug):
          print('Transforming par {}'.format(i))
        (proc, node.stmt[i]) = self.stmt_to_process(x)
        p.append(proc)
        p.extend(self.defn(proc))
    return p

  # Parallel replication
  def stmt_rep(self, node):
    p = self.stmt(node.stmt)
    if not isinstance(node.stmt, ast.StmtPcall):
      if(self.debug):
        print('Transforming rep')
      (proc, node.stmt) = self.stmt_to_process(node.stmt, node.indicies)
      p.append(proc)
      p.extend(self.defn(proc))
    return p

  # On
  def stmt_on(self, node):
    p = self.stmt(node.stmt)
    if not isinstance(node.stmt, ast.StmtPcall):
      if(self.debug):
        print('Transforming on')
      (proc, node.stmt) = self.stmt_to_process(node.stmt)
      p.append(proc)
      p.extend(self.defn(proc))
    return p

  def stmt_if(self, node):
    p = self.stmt(node.thenstmt)
    p += self.stmt(node.elsestmt)
    return p

  def stmt_while(self, node):
    return self.stmt(node.stmt)

  def stmt_for(self, node):
    return self.stmt(node.stmt)

  def stmt_skip(self, node):
    return []

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

  def stmt_return(self, node):
    return []

