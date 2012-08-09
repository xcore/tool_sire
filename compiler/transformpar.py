# Copyright (c) 2011, James Hanlon, All rights reserved
# This software is freely distributable under a derivative of the
# University of Illinois/NCSA Open Source License posted in
# LICENSE.txt and at <http://github.xcore.com/>

import copy
import ast
from util import debug
from walker import NodeWalker
from liveout import LiveOut
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
      
  def create_decl(self, elem):
    if elem.symbol.type == T_VAR_SINGLE:
      return ast.VarDecl(elem.name, T_VAR_SINGLE, None)
    
    elif elem.symbol.type == T_VAR_ARRAY:
      return ast.VarDecl(elem.name, T_VAR_ARRAY, elem.expr)
    
    elif elem.symbol.type == T_REF_ARRAY:
      return ast.VarDecl(elem.name, T_REF_ARRAY, None)
    
    elif elem.symbol.type == T_CHANEND_SINGLE:
     return ast.VarDecl(elem.name, T_CHANEND_SINGLE, None)
  
    elif elem.symbol.type == T_CHANEND_SERVER_SINGLE:
      return ast.VarDecl(elem.name, T_CHANEND_SERVER_SINGLE, None)
  
    elif elem.symbol.type == T_CHANEND_CLIENT_SINGLE:
      return ast.VarDecl(elem.name, T_CHANEND_CLIENT_SINGLE, None)
  
    else:
      print (elem.symbol.type)
      print (elem.name)
      assert 0

  def stmt_to_process(self, stmt, indices=[]):
    """
    Convert a statement into a process definition.
     - Create the definition node.
     - Create the corresponding Pcall node.
     - Insert the definition into the signature table.
     - Return the tuple (process-def, process-call)
    We pass process definitions recursively up the AST.

    Sets for live-in and local decls (for non-live, non-array targets). We want
    to add formal parameters for any live-in variable and for any variable that
    is both live-in and live-out, for a statement s::

      Live-over(s) = (live-in(s) | live-out(s)) & free(s)
    
    where | is set union and & is set intersection.
    
    Also, the index varible (rep_var) of replicator statements must be
    treated as a value and not a variable in its use as a parameter
    (transform replicator stage) and passed-by-reference.
    """
    assert isinstance(stmt, ast.Stmt)

    #out = set()
    #[out.update(y.inp) for y in succ.pred]
    #print('Successors: {}'.format(' '.join(['{}'.format(x.pred) for x in succ])))
    #[print(y.out) for y in succ.pred]

    out = LiveOut().compute(stmt)
    free = FreeVars().compute(stmt) 
    live = free & (stmt.inp | out)
    local_decls = free - live
    debug(self.debug, '==========================================')
    debug(self.debug, 'Free:        {}'.format(free))
    debug(self.debug, 'Live-in:     {}'.format(stmt.inp))
    debug(self.debug, 'Live-out:    {}'.format(out))
    debug(self.debug, 'live-over:   {}'.format(live))
    debug(self.debug, 'Local decls: {}'.format(local_decls)) 
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
    for x in indices:
      formals.append(ast.Param(x.name, T_VAL_SINGLE, None))
      formal_set.add(x)
      actuals.append(ast.ExprSingle(ast.ElemId(x.name)))
      live -= set([x])
      local_decls -= set([x])

    # Remove values from local declarations
    s = set()
    for x in local_decls:
      if not( x.symbol.type == T_VAL_SINGLE and \
          (x.symbol.scope == T_SCOPE_PROGRAM or \
            x.symbol.scope == T_SCOPE_SYSTEM)):
        s.add(x)
    local_decls = s

    # Replicated parallel statements are more restrivtive
    var_to_param = rep_var_to_param if len(indices)>0 else par_var_to_param
    
    # For each variable in the live-in set add accordingly to formals and actuals.
    for x in live:
      
      # Don't include constant values.
      if x.symbol.type == T_VAL_SINGLE and \
          (x.symbol.scope == T_SCOPE_PROGRAM or \
            x.symbol.scope == T_SCOPE_SYSTEM):
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
    [decls.append(self.create_decl(x)) for x in local_decls]
    
    # Create the new process definition
    if isinstance(stmt, ast.StmtSeq) or isinstance(stmt, ast.StmtPar):
      stmt.decls += decls
    else:
      stmt = ast.StmtSeq(decls, [stmt])
    d = ast.ProcDef(name, T_PROC, formals, stmt)

    # perform semantic analysis to update symbol bindings. 
    if self.debug:
      Printer().defn(d, 0)
    debug(self.debug, '==========================================')
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
      defs.extend(reversed(d))
      defs.append(x)
    node.defs = defs
  
  # Procedure definitions ===============================

  def defn(self, node):
    return self.stmt(node.stmt, []) if node.stmt else []
  
  # Statements ==========================================

  # Statements with paralellism

  # Parallel composition
  def stmt_par(self, node, indices):
    p = []
    p += self.stmt(node.stmt[0], indices)
    # We only need to transform statements [1:].
    for (i, x) in enumerate(node.stmt[1:]):
      if not isinstance(x, ast.StmtPcall):
        if(self.debug):
          print('Transforming par {} from {}'.format(i, x))
        (proc, node.stmt[i+1]) = self.stmt_to_process(x, indices)
        p.append(proc)
        p += self.stmt(proc.stmt, indices)
    return p

  # Server
  def stmt_server(self, node, indices):
    p = []
    p += self.stmt(node.server, indices)
    if not isinstance(node.client, ast.StmtPcall):
      if(self.debug):
        print('Transforming server client')
      (proc, node.client) = self.stmt_to_process(node.client, indices)
      p.append(proc)
      p += self.stmt(proc.stmt, indices)
    return p

  # Parallel replication
  def stmt_rep(self, node, indices):
    p = []
    if not isinstance(node.stmt, ast.StmtPcall):
      if(self.debug):
        print('Transforming rep')
      (proc, node.stmt) = self.stmt_to_process(node.stmt, indices+node.indices)
      p.append(proc)
      p += self.stmt(proc.stmt, indices+node.indices)
    return p

  # On
  def stmt_on(self, node, indices):
    p = []
    if not isinstance(node.stmt, ast.StmtPcall):
      if(self.debug):
        print('Transforming on')
      (proc, node.stmt) = self.stmt_to_process(node.stmt, indices)
      p.append(proc)
      p += self.stmt(proc.stmt, indices)
    return p

  # Regular statements

  def stmt_seq(self, node, indices):
    p = []
    [p.extend(self.stmt(x, indices)) for x in node.stmt]
    return p

  def stmt_if(self, node, indices):
    p = self.stmt(node.thenstmt, indices)
    p += self.stmt(node.elsestmt, indices)
    return p

  def stmt_while(self, node, indices):
    return self.stmt(node.stmt, indices)

  def stmt_for(self, node, indices):
    return self.stmt(node.stmt, indices)

  def stmt_skip(self, node, indices):
    return []

  def stmt_pcall(self, node, indices):
    return []

  def stmt_ass(self, node, indices):
    return []

  def stmt_in(self, node, indices):
    return []

  def stmt_out(self, node, indices):
    return []

  def stmt_in_tag(self, node, indices):
    return []

  def stmt_out_tag(self, node, indices):
    return []

  def stmt_alias(self, node, indices):
    return []

  def stmt_connect(self, node, indices):
    return []

  def stmt_assert(self, node, indices):
    return []

  def stmt_return(self, node, indices):
    return []

