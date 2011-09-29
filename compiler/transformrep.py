# Cmpyright (c) 2011, James Hanlon, All rights reserved
# This software is freely distributable under a derivative of the
# University of Illinois/NCSA Open Source License posted in
# LICENSE.txt and at <http://github.xcore.com/>

import copy
from math import floor
from functools import reduce
import util
import definitions as defs
import ast
from ast import NodeVisitor
from walker import NodeWalker
from formlocation import form_location
from freevars import FreeVars
from semantics import rep_var_to_param
from typedefs import *
from subelem import SubElem
from evalexpr import EvalExpr
from symbol import Symbol

from printer import Printer

class TransformRep(NodeWalker):
  """
  An AST walker to transform replicated parallel statements. We must check for
  existance of StmtRep nodes from parents so that they can be replaced.

  Example in two dimensions, from a process with a replicator:: 

   proc p(...) is
     ...
     par i in [0 for N], j in [2 for M] do q(i, j, ...)
     ...

  To the replicator replaced with a call to a distribution process::

    proc _d(_t, _n, _m, _b, params(_p)) is
      if n = 0
      then q((t/(M)) rem N), (t/y) rem M), ...)
      else if m > n/2
      then 
      { _d(t, n/2, n/2, _b, ...)
      | on (_b+((t+n/2)/F)) rem NUM_CORES) do
          _d(t+n/2, n/2, m-n/2, _b, ...)
      }
      else _d(t, n/2, m, _b, ...)

    proc p(...) is
      ...
      _d(0, next-pow-2(N*M), N*M, procid(), ...) 
      ...
  """
  def __init__(self, sym, sem, sig, device, debug=False):
    self.sym = sym
    self.sem = sem
    self.sig = sig
    self.device = device
    self.debug = debug

  def distribute_stmt(self, m, elem_t, elem_n, elem_m, base, 
        indicies, proc_actuals, formals, pcall):
    """
    Create the distribution process body statement.
    """

    # Setup some useful expressions
    name = self.sig.unique_process_name()
    elem_x = ast.ElemId('_x')
    expr_x = ast.ExprSingle(elem_x)
    expr_t = ast.ExprSingle(elem_t)
    expr_n = ast.ExprSingle(elem_n)
    expr_m = ast.ExprSingle(elem_m)
    elem_base = ast.ElemNumber(base) 
    expr_base = ast.ExprSingle(elem_base)

    # Replace ocurrances of index variables i with i = f(_t)
    divisor = m
    for x in indicies:
      divisor = floor(divisor / x.count_value)
      # Calculate the index i as a function of _t and the dimensions.
      e = ast.ExprBinop('rem', ast.ElemGroup(ast.ExprBinop('/', elem_t,
            ast.ExprSingle(ast.ElemNumber(divisor)))),
            ast.ExprSingle(ast.ElemNumber(x.count_value)))
      if x.base_value > 0:
        e = ast.ExprBinop('+', ast.ElemNumber(x.base_value),
            ast.ExprSingle(ast.ElemGroup(e)))
      # Then replace it for each ocurrance of i
      for y in pcall.args:
        y.accept(SubElem(ast.ElemId(x.name), ast.ElemGroup(e)))
 
    d = ast.ExprBinop('+', elem_t, ast.ExprSingle(elem_x))
    d = form_location(self.sym, elem_base, d, 1)

    # Create on the on statement
    on_stmt = ast.StmtOn(d,
        ast.StmtPcall(name,
          [ast.ExprBinop('+', elem_t, ast.ExprSingle(elem_x)), 
            expr_x, ast.ExprBinop('-', elem_m, ast.ExprSingle(elem_x))] 
            + proc_actuals))
    on_stmt.location = None

    # Conditionally recurse {d()|d()} or d()
    s1 = ast.StmtIf(
        # if m > n/2
        ast.ExprBinop('>', elem_m, ast.ExprSingle(elem_x)),
        # then
        ast.StmtPar([
            # on id()+t+n/2 do d(t+n/2, n/2, m-n/2, ...)
            on_stmt,
            # d(t, n/2, n/2)
            ast.StmtPcall(name, [expr_t, expr_x, expr_x] 
                + proc_actuals),
            ]),
        # else d(t, n/2, m)
        ast.StmtPcall(name, [expr_t, expr_x, expr_m] + proc_actuals))

    # _x = n/2 ; s1
    n_div_2 = ast.ExprBinop('>>', elem_n, ast.ExprSingle(ast.ElemNumber(1)))
    s2 = ast.StmtSeq([ast.StmtAss(elem_x, n_div_2), s1])

    # if n = 1 then process() else s1
    s3 = ast.StmtIf(ast.ExprBinop('=', elem_n,
      ast.ExprSingle(ast.ElemNumber(1))), pcall, s2)
  
    # Create the local declarations
    decls = [ast.Decl(elem_x.name, T_VAR_SINGLE, None)]

    # Create the definition
    d = ast.Def(name, T_PROC, formals, decls, s3)
    
    return d

  def transform_rep(self, stmt):
    """
    Convert a replicated parallel statement into a divide-and-conquer form.
     - Return the tuple (process-def, process-call)
    We only allow replicators where their location is known; i.e. stmt.location
    is an Expr(Number(x)).
    """
    assert isinstance(stmt, ast.StmtRep)
    assert isinstance(stmt.stmt, ast.StmtPcall)
    assert isinstance(stmt.location, ast.ExprSingle)
    assert isinstance(stmt.location.elem, ast.ElemNumber)
    pcall = stmt.stmt

    # The context of the procedure call is each variable occurance in the
    # set of arguments.
    context = FreeVars().compute(pcall)
    
    assert not stmt.m == None
    #assert not stmt.f == None
    n = util.next_power_of_2(stmt.m)

    # Create new variables
    formals = []       # Formals for the new distribution process
    actuals = []       # Actuals for the new distribution process
    proc_actuals = []  # All other live-in variables
    elem_t = ast.ElemId('_t') # Interval base
    elem_n = ast.ElemId('_n') # Interval width
    elem_m = ast.ElemId('_m') # Processes in interval
    #print(Printer().expr(stmt.location))
    base = stmt.location.elem.value

    # Populate the distribution and replicator indicies
    formals.append(ast.Param('_t', T_VAL_SINGLE, None))
    formals.append(ast.Param('_n', T_VAL_SINGLE, None))
    formals.append(ast.Param('_m', T_VAL_SINGLE, None))
    actuals.append(ast.ExprSingle(ast.ElemNumber(0)))
    actuals.append(ast.ExprSingle(ast.ElemNumber(n)))
    actuals.append(ast.ExprSingle(ast.ElemNumber(stmt.m)))
   
    # For each non-index free-variable of the process call
    for x in context - set([x for x in stmt.indicies]):
    
      # Add each unique variable ocurrance from context as a formal param
      formals.append(ast.Param(x.name, rep_var_to_param[x.symbol.type], 
          x.symbol.expr))
      
      # If the actual is an array subscript or slice, we only pass the id.
      if isinstance(x, ast.ElemSlice) or isinstance(x, ast.ElemSub):
        e = ast.ElemId(x.name)
        e.symbol = x.symbol
        proc_actuals.append(ast.ExprSingle(e))
      else:
        proc_actuals.append(ast.ExprSingle(copy.copy(x)))

    # Add the extra actual params to the distribution actuals
    actuals.extend(proc_actuals)

    # Create the process definition and perform semantic analysis to 
    # update symbol bindings. 
    d = self.distribute_stmt(stmt.m, elem_t, elem_n, elem_m, base,
                stmt.indicies, proc_actuals, formals, pcall)
    #Printer().defn(d, 0)
    self.sem.defn(d)
    
    # Create the corresponding call.
    c = ast.StmtPcall(d.name, actuals)
    self.sig.insert(d.type, d)
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
      defs.extend(d)
      defs.append(x)
    node.defs = defs
  
  # Procedure definitions ===============================

  def defn(self, node):
    if not node.stmt:
      return []
    p = self.stmt(node.stmt)
    if isinstance(node.stmt, ast.StmtRep):
      (d, node.stmt) = self.transform_rep(node.stmt)
      p.append(d)
    return p
  
  # Statements containing statements ====================

  def stmt_seq(self, node):
    p = []
    [p.extend(self.stmt(x)) for x in node.stmt]
    for (i, x) in enumerate(node.stmt):
      if isinstance(x, ast.StmtRep):
        (d, node.stmt[i]) = self.transform_rep(node.stmt[i])
        p.append(d)
    return p

  def stmt_par(self, node):
    p = []
    [p.extend(self.stmt(x)) for x in node.stmt]
    for (i, x) in enumerate(node.stmt):
      if isinstance(x, ast.StmtRep):
        (d, node.stmt[i]) = self.transform_rep(node.stmt[i])
        p.append(d)
    return p

  def stmt_server(self, node):
    p = self.stmt(node.server)
    p += self.stmt(node.client)
    if isinstance(node.server, ast.StmtRep):
      (d, node.server) = self.transform_rep(node.server)
      p.append(d)
    if isinstance(node.client, ast.StmtRep):
      (d, node.client) = self.transform_rep(node.client)
      p.append(d)
    return p

  def stmt_if(self, node):
    p = self.stmt(node.thenstmt)
    p += self.stmt(node.elsestmt)
    if isinstance(node.thenstmt, ast.StmtRep):
      (d, node.thenstmt) = self.transform_rep(node.thenstmt)
      p.append(d)
    if isinstance(node.elsestmt, ast.StmtRep):
      (d, node.elsestmt) = self.transform_rep(node.elsestmt)
      p.append(d)
    return p

  def stmt_while(self, node):
    p = self.stmt(node.stmt)
    if isinstance(node.stmt, ast.StmtRep):
      (d, node.stmt) = self.transform_rep(node.stmt)
      p.append(d)
    return p

  def stmt_for(self, node):
    p = self.stmt(node.stmt)
    if isinstance(node.stmt, ast.StmtRep):
      (d, node.stmt) = self.transform_rep(node.stmt)
      p.append(d)
    return p

  def stmt_rep(self, node):
    p = self.stmt(node.stmt)
    if isinstance(node.stmt, ast.StmtRep):
      (d, node.stmt) = self.transform_rep(node.stmt)
      p.append(d)
    return p

  def stmt_on(self, node):
    p = self.stmt(node.stmt)
    if isinstance(node.stmt, ast.StmtRep):
      (d, node.stmt) = self.transform_rep(node.stmt)
      p.append(d)
    return p

  # Statements ==========================================

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

  def stmt_connect(self, node):
    return []

  def stmt_assert(self, node):
    return []

  def stmt_return(self, node):
    return []

