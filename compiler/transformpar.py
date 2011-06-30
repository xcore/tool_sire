# Copyright (c) 2011, James Hanlon, All rights reserved
# This software is freely distributable under a derivative of the
# University of Illinois/NCSA Open Source License posted in
# LICENSE.txt and at <http://github.xcore.com/>

import copy
import ast
from walker import NodeWalker
from freevars import FreeVars
from typedefs import *
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

  def stmt_to_process(self, stmt, succ, indicies=[]):
    """
    Convert a statement into a process definition.
     - Create the definition node.
     - Create the corresponding Pcall node.
     - Insert the definition into the signature table.
     - Return the tuple (process-def, process-call)
   
    succ is the next statement (or the definiton which has a predecessor list)
    if there is not.

    Also, the index varible (rep_var) of replicator statements must be
    treated as a value and not a variable in its use as a parameter
    (transform replicator stage) and passed-by-reference.
    """
    assert isinstance(stmt, ast.Stmt)
    # Sets for live-in and local decls (for non-live, non-array targets).
    # Live-over = live-in u live-out
    # TODO: we want to add variables as parameters if (they are live in or live
    # out) and are used in the statement body.
    #print('Successors: {}'.format(' '.join(['{}'.format(x.pred) for x in succ])))
    out = set()
    [(out.update(y.out) for y in x.pred) for x in succ]
    
    free = FreeVars().allvars(stmt) 
    live = (stmt.inp | out) & free
    #print('Live (in and out): {}'.format(live))
    local_decls = free - live
    #Printer().stmt(stmt)

    # Create the formal and actual paramerer and local declaration lists
    formals = []
    formal_set = set()
    actuals = []
    decls = []

    # Deal with the index variable of a replicator statement: add it as a
    # single value (not a variable) to the formals and as-is to the actuals, 
    # then remove it from the variable live-in set and locals so it is not
    # declared again.
    for x in indicies:
      formals.append(ast.Param(x.name, T_VAL_SINGLE, None))
      formal_set.add(x)
      actuals.append(ast.ExprSingle(ast.ElemId(x.name)))
      live -= set([x])
      local_decls -= set([x])

    # Replicated parallel statements are more restrivtive
    var_to_param = rep_var_to_param if len(indicies)>0 else par_var_to_param
    
    # For each variable in the live-in set add accordingly to formals and actuals.
    for x in live:
      
      # Don't include constant values.
      if x.symbol.type == T_VAL_SINGLE and x.symbol.scope == 'program':
          continue
      
      # All parameters are added as formals with the appropriate conversion
      p = ast.Param(x.name, var_to_param[x.symbol.type], x.symbol.expr)
      p.symbol = x.symbol
      formals.append(p)
      formal_set.add(x)

      # If the actual is an array subscript or slice, we only pass the id.
      if isinstance(x, ast.ElemSlice) or isinstance(x, ast.ElemSub):
        e = ast.ElemId(x.name)
        e.symbol = x.symbol
        actuals.append(ast.ExprSingle(e))
      else:
        actuals.append(ast.ExprSingle(copy.copy(x)))
    
      # For arrays with lengths specified with variables (i.e. arrays passed by
      # reference) then we must include the length as the next parameter as long
      # as it is not already in the live set OR the formals and it's not a
      # defined value.
      if (x.symbol.type.form == 'array' 
          and isinstance(x.symbol.expr, ast.ExprSingle)
          and not x.symbol.expr.elem in live
          and not x.symbol.expr.elem in formal_set
          and x.symbol.value == None):
        p = ast.Param(x.symbol.expr.elem.name, T_VAL_SINGLE, None)
        formals.append(p)
        formal_set.add(x.symbol.expr.elem)
        actuals.append(x.symbol.expr)
      
    # Create a unique name
    name = self.sig.unique_process_name()

    # Create the local declarations (excluding values)
    for x in local_decls:
      if x.symbol.type == T_VAL_SINGLE:
        pass
        
      elif x.symbol.type == T_VAR_SINGLE:
        decls.append(ast.Decl(x.name, T_VAR_SINGLE, None))
      
      elif x.symbol.type == T_CHANEND_SINGLE:
        decls.append(ast.Decl(x.name, T_CHANEND_SINGLE, None))

      else:
        assert 0
    
    # Create the new process definition
    d = ast.Def(name, T_PROC, formals, decls, stmt)

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
    return self.stmt(node.stmt, [node]) if node.stmt else []
  
  # Statements ==========================================

  def stmt_seq(self, node, succ):
    p = []
    for (i, x) in enumerate(node.stmt):
      s = node.stmt[i+1] if i<len(node.stmt)-1 else succ
      p.extend(self.stmt(x, s)) 
    return p

  # Parallel composition
  def stmt_par(self, node, succ):
    """
    We only need to transform statements [1:].
    """
    p = []
    [p.extend(self.stmt(x, succ)) for x in node.stmt]
    for (i, x) in enumerate(node.stmt[1:]):
      if not isinstance(x, ast.StmtPcall):
        if(self.debug):
          print('Transforming par {}'.format(i))
        (proc, node.stmt[i+1]) = self.stmt_to_process(x, succ)
        p.append(proc)
        p.extend(self.defn(proc))
    return p

  # Parallel replication
  def stmt_rep(self, node, succ):
    p = self.stmt(node.stmt, succ)
    if not isinstance(node.stmt, ast.StmtPcall):
      if(self.debug):
        print('Transforming rep')
      (proc, node.stmt) = self.stmt_to_process(node.stmt, succ, node.indicies)
      p.append(proc)
      p.extend(self.defn(proc))
    return p

  # On
  def stmt_on(self, node, succ):
    p = self.stmt(node.stmt, succ)
    if not isinstance(node.stmt, ast.StmtPcall):
      if(self.debug):
        print('Transforming on')
      (proc, node.stmt) = self.stmt_to_process(node.stmt, succ)
      p.append(proc)
      p.extend(self.defn(proc))
    return p

  def stmt_if(self, node, succ):
    p = self.stmt(node.thenstmt, succ)
    p += self.stmt(node.elsestmt, succ)
    return p

  def stmt_while(self, node, succ):
    return self.stmt(node.stmt, succ)

  def stmt_for(self, node, succ):
    return self.stmt(node.stmt, succ)

  def stmt_skip(self, node, succ):
    return []

  def stmt_pcall(self, node, succ):
    return []

  def stmt_ass(self, node, succ):
    return []

  def stmt_in(self, node, succ):
    return []

  def stmt_out(self, node, succ):
    return []

  def stmt_alias(self, node, succ):
    return []

  def stmt_connect(self, node, succ):
    return []

  def stmt_return(self, node, succ):
    return []

