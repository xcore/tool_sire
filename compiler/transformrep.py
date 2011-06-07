# Copyright (c) 2011, James Hanlon, All rights reserved
# This software is freely distributable under a derivative of the
# University of Illinois/NCSA Open Source License posted in
# LICENSE.txt and at <http://github.xcore.com/>

import copy
from math import log, ceil, floor
import ast
from ast import NodeVisitor
from walker import NodeWalker
from freevars import FreeVars
from semantics import rep_var_to_param
from type import Type
from symbol import Symbol
from evalexpr import EvaluateExpr

from printer import Printer

class ReplaceElemInExpr(NodeVisitor):
    """
    Am AST walker to replace a particular element. Replace all instances of
    'old' element with 'new' element in the list of arguments.
    """
    def __init__(self, old, new):
        """
        Elements old and new.
        """
        self.old = old
        self.new = new

    def visit_expr_single(self, node):
        if isinstance(node.elem, type(self.old)):
            if node.elem.name == self.old.name:
                node.elem = self.new

    def visit_expr_unary(self, node):
        if isinstance(node.elem, type(self.old)):
            if node.elem.name == self.old.name:
                node.elem = self.new

    def visit_expr_binop(self, node):
        if isinstance(node.elem, type(self.old)):
            if node.elem.name == self.old.name:
                node.elem = self.new

class TransformRep(NodeWalker):
    """
    An AST walker to transform replicated parallel statements. We must check for
    existance of StmtRep nodes from parents so that they can be replaced.

    From:
        proc p(...) is
          ...
          rep <index> := <init> for <n> do _p0(..., <index>, ...)
          ...

    To:
        proc _dist(_t, _n, params(_p)) is
          if _n = 0 then 
              if _n<=<init>+<n> then
                _p1(..., _t+<init>, ...)
              else skip
          else 
          { _dist(_t, _n/2, params(_p))
          | _dist(_t+_n/2, _n/2, params(_p)) 
          }
        
        proc p(...) is
          ...
          _dist(0, next-pow-2(<n>-<init>), actuals(_p1)) 
          ...
    """
    def __init__(self, sem, sig, debug=False):
        self.sem = sem
        self.sig = sig
        self.debug = debug

    def distribute_stmt(self, elem_t, elem_n, elem_m, elem_b, 
            m, indicies, proc_actuals, formals, pcall):
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
        expr_b = ast.ExprSingle(elem_b)

        # Replace ocurrances of index variables i with i = f(_t)
        divisor = m
        for x in indicies:
            divisor = floor(divisor / x.count_value)
            for y in pcall.args:
                # Calculate the index i as a function of _t and the dimensions.
                e = ast.ElemGroup(
                        ast.ExprBinop('rem', ast.ElemGroup(ast.ExprBinop('/', elem_t,
                    ast.ElemNumber(divisor))), ast.ElemNumber(x.count_value)))
                # Then replace it for each ocurrance of i
                y.accept(ReplaceElemInExpr(ast.ElemId(x.name), e))
   
        # ((procid()+t+n/2) rem NUM_CORES
        d = ast.ExprBinop('rem', 
                ast.ElemGroup(ast.ExprBinop('+', elem_b,
                ast.ExprBinop('+', elem_t, elem_x))),
                ast.ElemId('NUM_CORES'))

        # Conditionally recurse {d()|d()} or d()
        s1 = ast.StmtIf(
                # if m > n/2
                ast.ExprBinop('>', elem_m, elem_x),
                # then
                ast.StmtPar([
                    # d(t, n/2, n/2)
                    ast.StmtPcall(name, [expr_t, expr_x, expr_x, expr_b] 
                        + proc_actuals),
                    # on ((id()+t+n/2) rem NUM_CORES) / f do 
                    #   d(t+n/2, n/2, m-n/2, ...)
                    ast.StmtOn(ast.ElemSub('core', d),
                        ast.StmtPcall(name,
                            [ast.ExprBinop('+', elem_t, elem_x), 
                            expr_x, ast.ExprBinop('-', elem_m, elem_x),
                            expr_b] + proc_actuals)
                        )
                    ]),
                # else d(t, n/2, m)
                ast.StmtPcall(name, [expr_t, expr_x, expr_m, expr_b] 
                        + proc_actuals))

        # _x = n/2 ; s1
        n_div_2 = ast.ExprBinop('>>', elem_n, ast.ElemNumber(1))
        s2 = ast.StmtSeq([ast.StmtAss(elem_x, n_div_2), s1])

        # if n = 0 then process() else s1
        s3 = ast.StmtIf(ast.ExprBinop('=', elem_n, ast.ElemNumber(0)), pcall, s2)
     
        # Create the local declarations
        decls = [ast.Decl(elem_x.name, Type('var', 'single'), None)]

        # Create the definition
        d = ast.Def(name, Type('proc', 'procedure'), formals, decls, s3)
        
        return d

    def next_power_of_2(self, n):
        return (2 ** ceil(log(n, 2)))

    def transform_rep(self, stmt):
        """
        Convert a replicated parallel statement into a divide-and-conquer form.
         - Return the tuple (process-def, process-call)
        """
        assert isinstance(stmt, ast.StmtRep)
        assert isinstance(stmt.stmt, ast.StmtPcall)
        pcall = stmt.stmt

        # The context of the procedure call is each variable occurance in the
        # set of arguments.
        context = FreeVars().allvars(pcall)
        #Printer().stmt(pcall)
        
        # Calculate total # processes (m) and the next power of two of this (n)
        m = stmt.indicies[0].count_value
        for x in stmt.indicies[1:]:
            m *= x.count_value
        n = self.next_power_of_2(m)
    
        # Create new variables
        T_VAL_SINGLE = Type('val', 'single')
        formals = []       # Formals for the new distribution process
        actuals = []       # Actuals for the new distribution process
        proc_actuals = []  # All other live-in variables
        elem_t = ast.ElemId('_t') # Interval base
        elem_n = ast.ElemId('_n') # Interval width
        elem_m = ast.ElemId('_m') # Processes in interval
        elem_b = ast.ElemId('_b') # Base address
        #elem_t.symbol = Symbol('_t', T_VAL_SINGLE)
        #elem_n.symbol = Symbol('_n', T_VAL_SINGLE)
        #elem_m.symbol = Symbol('_m', T_VAL_SINGLE)

        # Populate the distribution and replicator indicies
        formals.append(ast.Param('_t', T_VAL_SINGLE, None))
        formals.append(ast.Param('_n', T_VAL_SINGLE, None))
        formals.append(ast.Param('_m', T_VAL_SINGLE, None))
        formals.append(ast.Param('_b', T_VAL_SINGLE, None))
        actuals.append(ast.ExprSingle(ast.ElemNumber(0)))
        actuals.append(ast.ExprSingle(ast.ElemNumber(n)))
        actuals.append(ast.ExprSingle(ast.ElemNumber(m)))
        actuals.append(ast.ExprSingle(ast.ElemFcall('procid', [])))
       
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
        d = self.distribute_stmt(elem_t, elem_n, elem_m, elem_b,
                    m, stmt.indicies, proc_actuals, formals, pcall)
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
    
    # Statements ==========================================

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

