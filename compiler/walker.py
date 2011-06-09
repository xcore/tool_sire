# Copyright (c) 2011, James Hanlon, All rights reserved
# This software is freely distributable under a derivative of the
# University of Illinois/NCSA Open Source License posted in
# LICENSE.txt and at <http://github.xcore.com/>

import util

class NodeWalker(object):
  """
  A base class for walking an AST.
  """  
  def name(self, node):
    return util.camel_to_under(node.__class__.__name__)

  def decl(self, node, *args):
    f = getattr(self, '{}'.format(self.name(node)))
    return f(node, *args) if args else f(node)
  
  def defn(self, node, *args):
    f = getattr(self, '{}'.format(self.name(node)))
    return f(node, *args) if args else f(node)
  
  def param(self, node):
    f = getattr(self, '{}'.format(self.name(node)))
    return f(node)
  
  def stmt(self, node, *args):
    f = getattr(self, '{}'.format(self.name(node)))
    return f(node, *args) if args else f(node)
  
  def expr(self, node):
    f = getattr(self, '{}'.format(self.name(node)))
    return f(node)

  def elem(self, node):
    f = getattr(self, '{}'.format(self.name(node)))
    return f(node)

