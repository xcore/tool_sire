# Copyright (c) 2011, James Hanlon, All rights reserved
# This software is freely distributable under a derivative of the
# University of Illinois/NCSA Open Source License posted in
# LICENSE.txt and at <http://github.xcore.com/>

import copy
import ast
from walker import NodeWalker
from freevars import FreeVars
from type import Type
from semantics import var_to_param

from printer import Printer

class FlattenCalls(NodeWalker):
    """
    An AST walker to flatten nested calls:
    
    From:
        proc p(..) is
           q(...)

        proc r(...) is
            ...
            p(...)
            ...

    To:
        proc r(...) is
            ...
            q(...)
            ...

    Assert:
     - All process definitons occur before uses.
     - 'main' process is defined last, i.e. in ast.defs[-1]
    """
    def __init__(self, sig, debug=False):
        self.sig = sig
        self.debug = False

    # Program ============================================

    def walk_program(self, node):
        """
        Build a new list of definitions with new process definitons occuring
        before their use. Flattened processes are removed from the signature
        table. We don't consider the main process. 
        """
        defs = []
        replace = []
        for x in node.defs[:-1]:
            if self.defn(x, replace):
                self.sig.remove(replace[-1][0])
            else:
                defs.append(x)
        defs.append(node.defs[-1])
        node.defs = defs
    
    # Procedure definitions ===============================

    def defn(self, node, replace):
        """
        Look for processes with nested calls which have the structure:
        
            proc ... is
                p(...)
    
        or

            proc ... is
              { p(...) }
        """
        if isinstance(node.stmt, ast.StmtPcall): 
            if(self.debug):
                print('Found nested call in '+node.name)
            replace.append((node.name, node.stmt))
            return True
        elif (isinstance(node.stmt, ast.StmtSeq) and 
                isinstance(node.stmt.stmt[0], ast.StmtPcall)):
            if(self.debug):
                print('Found nested (seq) call in '+node.name)
            replace.append((node.name, node.stmt.stmt[0]))
            return True
        else:
            self.stmt(node.stmt, replace)
            return False
    
    # Statements ==========================================

    def stmt_seq(self, node, replace):
        [self.stmt(x, replace) for x in node.stmt]

    def stmt_par(self, node, replace):
        [self.stmt(x, replace) for x in node.stmt]

    def stmt_pcall(self, node, replace):
        """
        For a pcall matching a replacement name, replace the call.
        """
        for (name, pcall) in replace:
            if node.name == name:
                if(self.debug):
                    print('Replacing pcall '+name+' with '+pcall.name)
                node.name = pcall.name
                node.args = pcall.args

    def stmt_if(self, node, replace):
        self.stmt(node.thenstmt, replace)
        self.stmt(node.elsestmt, replace)

    def stmt_while(self, node, replace):
        self.stmt(node.stmt, replace)

    def stmt_for(self, node, replace):
        self.stmt(node.stmt, replace)

    def stmt_rep(self, node, replace):
        self.stmt(x, replace)

    def stmt_skip(self, node, replace):
        pass

    def stmt_ass(self, node, replace):
        pass

    def stmt_alias(self, node, replace):
        pass

    def stmt_on(self, node, replace):
        pass

    def stmt_return(self, node, replace):
        pass

