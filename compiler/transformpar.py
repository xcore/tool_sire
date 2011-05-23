# Copyright (c) 2011, James Hanlon, All rights reserved
# This software is freely distributable under a derivative of the
# University of Illinois/NCSA Open Source License posted in
# LICENSE.txt and at <http://github.xcore.com/>

import copy
import ast
from walker import NodeWalker
from type import Type
from semantics import var_to_param

from printer import Printer

class TransformPar(NodeWalker):
    """
    An AST walker to transform parallel blocks. 
    """
    def __init__(self, sig, debug=False):
        self.sig = sig
        self.debug = False

    def stmt_to_process(self, stmt, rep_var=None):
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
        # The context of parallel statement is the union of the set of incoming
        # live variables and each occuance of an array identifier in the
        # statement block.
        #context = Context().run(stmt) | stmt.inp
        context = stmt.inp
        #Printer().stmt(stmt)
        #print(context)
        
        # Create the formal and actual paramerer lists
        formals = []
        actuals = []

        # Deal with the index variable of a replicator statement: add it as a
        # single value to the formals and as-is to the actuals, then remove it
        # from the variable context.
        #if rep_var:
        #    formals.append(ast.Param(rep_var.name, Type('val', 'single'), 
        #        None))
        #    actuals.append(ast.ExprSingle(copy.copy(rep_var)))
        #    context = context - set([rep_var])

        # For each variable in the context add accordingly to formals and actuals.
        for x in context:
            formals.append(ast.Param(x.name, var_to_param[x.symbol.type], 
                x.symbol.expr))
            
            # If the actual is an array subscript or slice, we only pass the id.
            if isinstance(x, ast.ElemSlice) or isinstance(x, ast.ElemSub):
                elem = ast.ElemId(x.name)
                elem.symbol = x.symbol
                actuals.append(ast.ExprSingle(elem))
            else:
                actuals.append(ast.ExprSingle(copy.copy(x)))
        
        # Create a unique name
        name = self.sig.unique_process_name()

        # Create the definition and corresponding call.
        d = ast.Def(name, Type('proc', 'procedure'), formals, [], stmt)
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
        return self.stmt(node.stmt)
    
    # Statements ==========================================

    def stmt_seq(self, node):
        p = []
        [p.extend(self.stmt(x)) for x in node.stmt]
        return p

    def stmt_par(self, node):
        p = []
        for (i, x) in enumerate(node.stmt):
            if not isinstance(x, ast.StmtPcall):
                if(self.debug):
                    print('Transforming par {}'.format(i))
                (proc, node.stmt[i]) = self.stmt_to_process(x)
                p.append(proc)
                p.extend(self.defn(node.proc))
        return p

    def stmt_skip(self, node):
        return []

    def stmt_pcall(self, node):
        return []

    def stmt_ass(self, node):
        return []

    def stmt_alias(self, node):
        return []

    def stmt_if(self, node):
        p = self.stmt(node.thenstmt)
        p += self.stmt(node.elsestmt)
        return p

    def stmt_while(self, node):
        return self.stmt(node.stmt)

    def stmt_for(self, node):
        return self.stmt(node.stmt)

    def stmt_rep(self, node):
        p = []
        if not isinstance(node.stmt, ast.StmtPcall):
            if(self.debug):
                print('Transforming rep')
            (proc, node.stmt) = self.stmt_to_process(node.stmt, node.var)
            p.append(proc)
            p.extend(self.defn(proc))
        return p

    def stmt_on(self, node):
        return []

    def stmt_return(self, node):
        return []

