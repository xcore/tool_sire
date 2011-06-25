# Copyright (c) 2011, James Hanlon, All rights reserved
## This software is freely distributable under a derivative of the
## University of Illinois/NCSA Open Source License posted in
## LICENSE.txt and at <http://github.xcore.com/>

import sys
import copy
import collections
from itertools import product

import ast
from walker import NodeWalker
from typedefs import *
from subelem import SubElem
from evalexpr import EvalExpr

from printer import Printer

class LabelChans(NodeWalker):
  """
  Label channel uses. For replicators, expand array subscripts over the range
  of the iterators and tag each with its offset relative to the declaration of
  the channel. Then label each channel with the relative offset from the master
  to the slave.
  """
  def __init__(self, print_debug=True):
    self.print_debug = print_debug

  def debug(self, s):
    if self.print_debug:
      print(s)
  
  def chankey(self, name, index):
    return '{}{}'.format(name, index)

  def expand_channel(self, iterators, labels, stmt, elem):
    """
    Expand the use of a channel subscript over a set of iterators.
    """
    #print(Printer().expr(elem.expr))
    #print(Printer().expr(stmt.location))
    ranges = [range(x.base_value, x.base_value+x.count_value) for x in iterators]
    for x in product(*ranges):
      index_expr = copy.deepcopy(elem.expr)
      locat_expr = copy.deepcopy(stmt.location)
      for (y, z) in zip(iterators, x):
        index_expr.accept(SubElem(ast.ElemId(y.name), ast.ElemNumber(z)))
        locat_expr.accept(SubElem(ast.ElemId(y.name), ast.ElemNumber(z)))
      #print(Printer().expr(locat_expr))
      index_value = EvalExpr().expr(index_expr)
      locat_value = EvalExpr().expr(locat_expr)
      self.debug('  {}[{}] at {}'.format(elem.name, index_value, locat_value))
     
      # Add the locations to the label table
      key = self.chankey(elem.name, index_value) 
      if not key in labels:
        labels[key] = []
      labels[key].append(locat_value)

  # Program ============================================

  def walk_program(self, node):
    #[self.decl(x) for x in node.decls]
    [self.defn(x) for x in node.defs]
  
  # Procedure definitions ===============================

  def defn(self, node):
    #[self.decl(x) for x in node.decls]
    self.debug('New channel scope: '+node.name)
    iterators = []
    labels = {}
    self.stmt(node.stmt, iterators, labels)
    self.debug('Channel label table:')
    for x in labels.keys():
      self.debug('  {}: {}'.format(x, ', '.join(['{}'.format(y) for y in labels[x]])))
  
  # Statements ==========================================

  # Statements containing uses of channels

  def stmt_in(self, node, iterators, labels):
    self.debug('out channel {}:'.format(node.left.name))
    if isinstance(node.left, ast.ElemSub):
      self.expand_channel(iterators, labels, node, node.left)
    elif isinstance(node.left, ast.ElemId):
      assert 0

  def stmt_out(self, node, iterators, labels):
    self.debug('in channel {}:'.format(node.left.name))
    if isinstance(node.left, ast.ElemSub):
      self.expand_channel(iterators, labels, node, node.left)
    elif isinstance(node.left, ast.ElemId):
      assert 0

  def stmt_pcall(self, node, iterators, labels):
    for x in node.args:
      if (isinstance(x, ast.ExprSingle) 
          and isinstance(x.elem, ast.ElemSub)
          and x.elem.symbol.type == T_CHAN_ARRAY):
        self.debug('arg channel {}:'.format(x.elem.name))
        self.expand_channel(iterators, labels, node, x.elem)
    
  # Statements containing processes

  def stmt_rep(self, node, iterators, labels):
    self.stmt(node.stmt, iterators + node.indicies, labels)
  
  def stmt_seq(self, node, iterators, labels):
    [self.stmt(x, iterators, labels) for x in node.stmt]

  def stmt_par(self, node, iterators, labels):
    [self.stmt(x, iterators, labels) for x in node.stmt]

  def stmt_if(self, node, iterators, labels):
    self.stmt(node.thenstmt, iterators, labels)
    self.stmt(node.elsestmt, iterators, labels)

  def stmt_while(self, node, iterators, labels):
    self.stmt(node.stmt, iterators, labels)

  def stmt_for(self, node, iterators, labels):
    self.stmt(node.stmt, iterators, labels)

  # Statements not containing processes or channels uses

  def stmt_ass(self, node, iterators, labels):
    pass

  def stmt_alias(self, node, iterators, labels):
    pass

  def stmt_skip(self, node, iterators, labels):
    pass

  def stmt_return(self, node, iterators, labels):
    pass

  # Prohibited statements

  def stmt_on(self, node, iterators, labels):
    assert 0

  def stmt_connect(self, node, iterators, labels):
    assert 0

