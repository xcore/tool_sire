# Copyright (c) 2011, James Hanlon, All rights reserved
# This software is freely distributable under a derivative of the
# University of Illinois/NCSA Open Source License posted in
# LICENSE.txt and at <http://github.xcore.com/>

import copy
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

    def distribute_stmt(self, name, elem_t, elem_n, elem_m, index_actuals, proc_actuals, pcall):
        """
        Create the distribution process body statement.
        """
        expr_zero = ast.ExprSingle(ast.ElemNumber(0))
        expr_two  = ast.ExprSingle(ast.ElemNumber(2))
        n_div_2   = ast.ExprBinop('/', elem_n, expr_two)

        s1 = ast.StmtSkip()
            #ast.StmtIf()
            #    ast.StmtPar([
            #        ast.StmtPcall(name, [ast.ExprSingle(elem_t), n_div_2] 
            #            + index_actuals + proc_actuals),
            #        ast.StmtPcall(name, [ast.ExprBinop('+', elem_t,
            #            ast.ElemGroup(n_div_2)), n_div_2] 
            #            + index_actuals + proc_actuals)
            #        ]))

        #s1 = ast.StmtIf(ast.ExprBinop('=', elem_n, expr_zero), pcall, s2)
        
        return s1

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
        
        # Create new variables _t and _n.
        elem_t = ast.ElemId('_t')
        elem_n = ast.ElemId('_n')
        elem_m = ast.ElemId('_m')
        elem_t.symbol = Symbol('_t', Type('val', 'single'))
        elem_n.symbol = Symbol('_n', Type('val', 'single'))
        elem_m.symbol = Symbol('_m', Type('val', 'single'))

        # TODO Replace ocurrances of index variable in Pcall with _t
        #for x in pcall.args:
        #    x.accept(ReplaceElemInExpr(pcall, elem_t))

        formals = []       # Formals for the new distribution process
        actuals = []       # Actuals for the new distribution process
        index_actuals = [] # Index variables from the replicator
        proc_actuals = []  # All other live-in variables

        # Populate the distribution and replicator indicies
        formals.append(ast.Param('_t', Type('val', 'single'), None))
        actuals.append(ast.ExprSingle(ast.ElemNumber(0)))
        formals.append(ast.Param('_n', Type('val', 'single'), None))
        actuals.append(ast.ExprSingle(ast.ElemNumber(0)))
        formals.append(ast.Param('_m', Type('val', 'single'), None))
        actuals.append(ast.ExprSingle(ast.ElemNumber(0)))
        for x in stmt.indicies:
            index_actuals.append(ast.ExprSingle(ast.ElemId(x.name)))
            #print(x.count_value)
       
        # Add each unique variable ocurrance from context as a formal param
        for x in context - set([x for x in stmt.indicies]):
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

        # Create the process definition 
        name = self.sig.unique_process_name()
        d = ast.Def(name, Type('proc', 'procedure'), 
                formals, [], self.distribute_stmt(name, elem_t, elem_n, elem_m,
                    index_actuals, proc_actuals, pcall))

        # Perform semantic analysis to update symbol bindings. 
        self.sem.defn(d)
        
        # Create the corresponding call.
        c = ast.StmtPcall(name, actuals)
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

