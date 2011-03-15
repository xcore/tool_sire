# Copyright (c) 2011, James Hanlon, All rights reserved
# This software is freely distributable under a derivative of the
# University of Illinois/NCSA Open Source License posted in
# LICENSE.txt and at <http://github.xcore.com/>

import sys
import builtin
from ast import NodeVisitor

class Children(NodeVisitor):
    """ An AST walker class to determine the children of each procedure
    """
    
    def __init__(self, proc_names):
        self.parent = None
        self.children = {}
        for x in proc_names:
            self.children[x] = []

    def up(self, tag):
        pass

    def down(self, tag):
        pass

    def add_child(self, name):
        """ Add a child procedure call of the program:
             - omit builtins
             - add only if it hasn't been already
             - don't add if it is its parent (recursive)
        """
        if ((not name in builtin.names) 
                and (not name in self.children[self.parent])
                and (not name == self.parent)):
            self.children[self.parent].append(name)
            #print('added child '+name+' to '+self.parent)

    def build(self):
        """ Given immediate child relationships, calculate all nested
            relationships
        """
        change = True
        # While there are still changes
        while change:
            change = False
            # For each procedure x
            for x in self.children.keys():
                # For each child call y of x
                for y in self.children[x]:
                    # for each child z of call y, or grandchild of x
                    for z in self.children[y]:
                        # Add it if it hasn't already been
                        if not z in self.children[x]:
                            self.children[x].append(z)
                            change = True

    def display(self, buf=sys.stdout):
        """ Display children """
        for x in self.children.keys():
            buf.write(x+':\n')
            if x in self.children:
                for y in self.children[x]:
                    buf.write('\t'+y+'\n')

    def visit_def(self, node):
        self.parent = node.name
        return 'proc'
    
    def visit_stmt_pcall(self, node):
        self.add_child(node.name)

    def visit_elem_fcall(self, node):
        self.add_child(node.name)

