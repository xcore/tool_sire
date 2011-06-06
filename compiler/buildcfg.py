# Copyright (c) 2011, James Hanlon, All rights reserved
# This software is freely distributable under a derivative of the
# University of Illinois/NCSA Open Source License posted in
# LICENSE.txt and at <http://github.xcore.com/>

import ast
from walker import NodeWalker

class BuildCFG(NodeWalker):
    """
    A NodeWalker to build the Control-Flow Graph for the AST. 
     - For statements: set predecessor and successor lists and populate the use,
       def, in and out sets for liveness analysis.
     - For expressions return a set of used variable elements.
    """
    def __init__(self):
        pass

    def init_sets(self, node, pred, succ):
        node.pred = pred
        node.succ = succ
        node.use = set()
        node.defs = set()
        node.inp = set()
        node.out = set()

    def run(self, node):
        """
        Walk each procedure definition.
        """
        [self.defn(x) for x in node.defs]
   
    def defn(self, node):
        """
    `   Before traversing the body statement we add arrays to an implicit uses
        set. Arrays are used implicitly by every statement as their live range
        is the entire procedure.
        """
        if node.stmt:
            self.stmt(node.stmt, [], [])

    # Statements ==========================================

    def stmt_seq(self, node, pred, succ):
        self.init_sets(node, pred, [node.stmt[0]])
        for (i, x) in enumerate(node.stmt):
            p = [node.stmt[i-1]] if i>0 else pred
            s = [node.stmt[i+1]] if i<len(node.stmt)-1 else succ
            self.stmt(x, p, s) 

    def stmt_par(self, node, pred, succ):
        self.init_sets(node, pred, succ)
        [self.stmt(x, pred, succ) for x in node.stmt]

    def stmt_skip(self, node, pred, succ):
        self.init_sets(node, pred, succ)

    def stmt_pcall(self, node, pred, succ):
        self.init_sets(node, pred, succ)
        [node.use.update(self.expr(x)) for x in node.args]

    def stmt_ass(self, node, pred, succ):
        self.init_sets(node, pred, succ)
        node.use |= self.expr(node.expr)
        node.defs |= set([node.left])

        # Writes to arrays, include them as a use so they are live until this
        # point.
        if isinstance(node.left, ast.ElemSub):
            node.use |= node.defs

    def stmt_alias(self, node, pred, succ):
        self.init_sets(node, pred, succ)
        node.use |= self.expr(node.expr)
        node.defs |= set([node.left])

        # Add alias targets to use set to they are live until this point.
        node.use |= node.defs 

    def stmt_if(self, node, pred, succ):
        self.init_sets(node, pred, [node.thenstmt, node.elsestmt])
        self.stmt(node.thenstmt, [node], succ)
        self.stmt(node.elsestmt, [node], succ)
        node.use |= self.expr(node.cond)

    def stmt_while(self, node, pred, succ):
        self.init_sets(node, pred, [node.stmt])
        self.stmt(node.stmt, [node], [node]+succ)
        node.use |= self.expr(node.cond)

    def stmt_for(self, node, pred, succ):
        self.init_sets(node, pred, [node.stmt])
        self.stmt(node.stmt, [node], [node]+succ)
        node.defs |= set([node.var])
        node.use |= self.expr(node.init)
        node.use |= self.expr(node.bound)
        node.use |= self.expr(node.step)

    def stmt_rep(self, node, pred, succ):
        self.init_sets(node, pred, [node.stmt])
        self.stmt(node.stmt, pred, succ)
        node.defs |= set([x.name for x in node.indicies])
        [node.use.append(self.expr(x.init)) for x in node.indicies]
        [node.use.append(self.expr(x.count)) for x in node.indicies]

    def stmt_on(self, node, pred, succ):
        self.init_sets(node, pred, succ)
        self.stmt(node.stmt, [node], [node])

    def stmt_return(self, node, pred, succ):
        self.init_sets(node, pred, succ)
        node.use |= self.expr(node.expr)
    
    # Expressions =========================================

    def expr_single(self, node):
        return self.elem(node.elem)

    def expr_unary(self, node):
        return self.elem(node.elem)

    def expr_binop(self, node):
        c = self.elem(node.elem)
        c |= self.expr(node.right)
        return c
    
    # Elements= ===========================================

    # Identifier
    def elem_id(self, node):
        return set([node])

    # Array subscript
    def elem_sub(self, node):
        c = self.expr(node.expr)
        return c | set([node])

    # Array slice
    def elem_slice(self, node):
        c = self.expr(node.begin)
        c |= self.expr(node.end)
        return c | set([node])

    # Index
    def elem_index(self, node):
        node.defs |= set([node.name])
        node.use |= self.expr(node.init)
        node.use |= self.expr(node.count)

    def elem_group(self, node):
        return self.expr(node.expr)

    def elem_pcall(self, node):
        c = set()
        [c.append(self.expr(x)) for x in node.args]
        return c

    def elem_fcall(self, node):
        c = set()
        [c.append(self.expr(x)) for x in node.args]
        return c

    def elem_number(self, node):
        return set()

    def elem_boolean(self, node):
        return set()

    def elem_string(self, node):
        return set()

    def elem_char(self, node):
        return set()


