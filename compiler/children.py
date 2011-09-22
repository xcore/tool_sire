# Copyright (c) 2011, James Hanlon, All rights reserved
# This software is freely distributable under a derivative of the
# University of Illinois/NCSA Open Source License posted in
# LICENSE.txt and at <http://github.xcore.com/>

import sys

from ast import NodeVisitor
from builtin import builtins

class Children(NodeVisitor):
  """
  An AST visitor to determine the children of each procedure.
  """
  def __init__(self, sig, debug=False):
    self.debug = debug
    self.parent = None
    self.children = {}
    for x in sig.mobile_proc_names:
      self.children[x] = []

  def add_child(self, name):
    """ 
    Add a child procedure call of the program:
     - omit non-mobile builtins
     - add only if it hasn't been already
     - don't add if it is its parent (recursive)
    """
    if ((not name in self.children[self.parent]) and name != self.parent
        and not name in filter(lambda x: not builtins[x].mobile, builtins.keys())):
      self.children[self.parent].append(name)
      if(self.debug):
        print('  added child '+name+' to '+self.parent)

  def build(self):
    """ 
    Given immediate child relationships, calculate all nested relationships.
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
            if not z in self.children[x] and x != z:
              self.children[x].append(z)
              change = True

  def display(self, buf=sys.stdout):
    """
    Display children.
    """
    for x in self.children.keys():
      buf.write(x+':\n')
      if x in self.children:
        for y in self.children[x]:
          buf.write('\t'+y+'\n')
      buf.write('\n')

  def visit_def(self, node):
    if self.debug:
      print('Definition: '+node.name)
    self.parent = node.name
    return 'proc'
  
  def visit_stmt_pcall(self, node):
    if self.debug:
      print('  visiting pcall '+node.name)
    self.add_child(node.name)

  def visit_elem_fcall(self, node):
    if self.debug:
      print('  visiting fcall '+node.name)
    self.add_child(node.name)

