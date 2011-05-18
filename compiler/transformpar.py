# Copyright (c) 2011, James Hanlon, All rights reserved
# This software is freely distributable under a derivative of the
# University of Illinois/NCSA Open Source License posted in
# LICENSE.txt and at <http://github.xcore.com/>

import ast
from walker import NodeWalker
from context import Context
from type import Type
from semantics import var_to_param

class TransformPar(NodeWalker):
    """
    An AST walker to transform parallel blocks. 
    """
    def __init__(self, sig, debug=False):
        self.sig = sig
        self.debug = debug

    def stmt_to_process(self, stmt):
        """
        Convert a statement into a process definition.
         - Create the definition node.
         - Create the corresponding Pcall node.
         - Insert the definition into the signature table.
        """
        context = Context().walk_stmt(stmt)
        #print(', '.join([x[0] for x in context]))
        #print(', '.join(['{}'.format(x[1]) for x in context]))
        
        # Create the formal and actual paramerer lists
        formals = []
        actuals = []
        for x in context:
            formals.append(ast.Param(x.name, var_to_param[x.symbol.type], 
                x.symbol.expr))
            
            # If the actual is a slice, we only want to pass the array id.
            if isinstance(x, ast.ElemSlice):
                elem = ast.ElemId(x.name)
                elem.symbol = x.symbol
                actuals.append(ast.ExprSingle(elem))
            else:
                actuals.append(x)
        
        # Create a unique name
        name = '_a'
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
                    print('Transforming stmt {}'.format(i))
                (proc, pcall) = self.stmt_to_process(x)
                node.stmt[i] = pcall
                p.append(proc)
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
        return self.elem(node.stmt)

    def stmt_on(self, node):
        return []

    def stmt_return(self, node):
        return []

