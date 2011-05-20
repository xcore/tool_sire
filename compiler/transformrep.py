# Copyright (c) 2011, James Hanlon, All rights reserved
# This software is freely distributable under a derivative of the
# University of Illinois/NCSA Open Source License posted in
# LICENSE.txt and at <http://github.xcore.com/>

import copy
import ast
from ast import NodeVisitor
from walker import NodeWalker
from semantics import var_to_param
from context import Context
from type import Type
from symbol import Symbol

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
    """
    def __init__(self, sig, debug=False):
        self.sig = sig
        self.debug = debug

    def transform_rep(self, stmt):
        """
        Convert a replicated parallel statement into a divide-and-conquer form.
         - Return the tuple (process-def, process-call)
        """
        assert isinstance(stmt, ast.StmtRep)
        assert isinstance(stmt.stmt, ast.StmtPcall)
        context = Context().walk_stmt(stmt.stmt)
        #Printer().stmt(stmt)
        #print(context)
        
        # Create new variables _t and _n.
        elem_t = ast.ElemId('_t')
        elem_n = ast.ElemId('_n')
        elem_t.symbol = Symbol('_t', Type('val', 'single'))
        elem_n.symbol = Symbol('_n', Type('val', 'single'))

        # Replace ocurrances of index variable in Pcall with _t
        for x in stmt.stmt.args:
            x.accept(ReplaceElemInExpr(stmt.var, elem_t))

        # Create the formal and actual paramerer lists for distribution
        formals = []
        actuals = []
        formals.append(ast.Param('_t', Type('val', 'single'), None))
        formals.append(ast.Param('_n', Type('val', 'single'), None))
        actuals.append(ast.ExprSingle(ast.ElemNumber(0)))
        actuals.append(stmt.count)
        
        # List of actual parameters (not including the index) for the pcall
        proc_actuals = []
       
        # Add each unique variable ocurrance from context as a formal param
        for x in context - set([stmt.var]):
            formals.append(ast.Param(x.name, var_to_param[x.symbol.type], 
                x.symbol.expr))
            
            # If the actual is an array subscript or slice, we only pass the id.
            if isinstance(x, ast.ElemSlice) or isinstance(x, ast.ElemSub):
                elem = ast.ElemId(x.name)
                elem.symbol = x.symbol
                proc_actuals.append(ast.ExprSingle(elem))
            else:
                proc_actuals.append(ast.ExprSingle(copy.copy(x)))

        # Add the extra actual params to the distribution actuals
        actuals.extend(proc_actuals)
       
        # Create the distribution process body statement 
        name = self.sig.unique_process_name()
        n_div_2 = ast.ExprBinop('/', elem_n, ast.ExprSingle(ast.ElemNumber(2)))
        s = ast.StmtIf(
                ast.ExprBinop('=', elem_n, ast.ExprSingle(ast.ElemNumber(0))),
                stmt.stmt,
                ast.StmtPar([
                    ast.StmtPcall(name, [ast.ExprSingle(elem_t), n_div_2] +
                        proc_actuals),
                    ast.StmtPcall(name, [ast.ExprBinop('+', elem_t,
                        ast.ElemGroup(n_div_2)), n_div_2] + proc_actuals)
                    ]))
        d = ast.Def(name, Type('proc', 'procedure'), formals, [], s)
        c = ast.StmtPcall(name, actuals)
        self.sig.insert(d.type, d)
        return (d, c)

    # Program ============================================

    def walk_program(self, node):
        p = []
        [p.extend(self.defn(x)) for x in node.defs]
        [node.defs.insert(0, x) for x in reversed(p)]
    
    # Procedure definitions ===============================

    def defn(self, node):
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

    def stmt_skip(self, node):
        return []

    def stmt_pcall(self, node):
        return []

    def stmt_ass(self, node):
        return []

    def stmt_alias(self, node):
        return []

    def stmt_on(self, node):
        return []

    def stmt_return(self, node):
        return []

