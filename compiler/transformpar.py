# Copyright (c) 2011, James Hanlon, All rights reserved
# This software is freely distributable under a derivative of the
# University of Illinois/NCSA Open Source License posted in
# LICENSE.txt and at <http://github.xcore.com/>

import ast
from walker import NodeWalker
from type import Type

class TransformPar(NodeWalker):
    """
    An AST walker to transform parallel blocks. 
    """
    def __init__(self):
        pass

    def stmt_to_process(self, stmt):
        """
        Convert a statement into a process definition.
        """
        return (ast.Def('a', Type('proc', 'procedure'), [], [], ast.StmtSkip()), 
            ast.StmtPcall('a', []))

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
        [p.extend(self.stmt(x)) for x in node.children()]
        return p

    def stmt_par(self, node):
        p = []
        for (i, x) in enumerate(node.stmt):
            if not isinstance(x, ast.StmtPcall):
                print('Transforming stmt {}'.format(i))
                (proc, pcall) = self.stmt_to_process(x)
                node.stmt[i] = pcall
                #p.append(node.stmt[i])
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

