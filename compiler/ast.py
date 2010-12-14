class Node:
    def __init__(self, type, children=None, leaf=None):
         self.type = type
         if children:
              self.children = children
         else:
              self.children = [ ]
         self.leaf = leaf
     
