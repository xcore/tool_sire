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
  For each procedure definition, construct a table which records for each use
  of a channel the offsets of the master and slave processes (relative to the
  base). For replicators, expand array subscripts over the range of the
  iterators and tag each with its offset relative to the declaration of the
  channel. Then label each channel with the relative offset from the master to
  the slave.
  """
  def __init__(self, print_debug=False):
    self.print_debug = print_debug

  def debug(self, s):
    if self.print_debug:
      print(s)
  
  def chankey(self, name, index):
    """
    Given a channel name and its index return a key concatenating these.
    """
    return '{}{}'.format(name, '' if index==None else index)

  def tab_insert(self, tab, name, index, offset):
    """
    Add the locations to the label table.
    """
    key = self.chankey(name, index)
    if not key in tab:
      tab[key] = []
    tab[key].append(offset)

  def single_channel(self, tab, stmt, elem):
    """
    Process a single (non-subscripted) channel use by evaluating its location
    and then adding it to the channel table and returning its use tuple. The
    location will not contain any variables.
    """
    offset_value = EvalExpr().expr(stmt.location)
    self.debug('  {} at {}'.format(elem.name, offset_value))
    self.tab_insert(tab, elem.name, None, offset_value)
    return (elem.name, None)

  def subscript_channel(self, iters, tab, stmt, elem):
    """
    Expand the use of a channel subscript over a set of iterators and determine
    for each the value of its index and location, and then add this to the
    channel table and set of uses.
    """
    #print(Printer().expr(elem.expr))
    #print(Printer().expr(stmt.location))
    uses = []

    # Iterate over cartesian product of iterator ranges
    ranges = [range(x.base_value, x.base_value+x.count_value) for x in iters]
    for x in product(*ranges):

      # Deep copy expressions so we can modify them
      index_expr = copy.deepcopy(elem.expr)
      locat_expr = copy.deepcopy(stmt.location)

      # Substitute index variables for values
      for (y, z) in zip(iters, x):
        index_expr.accept(SubElem(ast.ElemId(y.name), ast.ElemNumber(z)))
        locat_expr.accept(SubElem(ast.ElemId(y.name), ast.ElemNumber(z)))

      # Evaluate the expressions
      index_value = EvalExpr().expr(index_expr)
      offset_value = EvalExpr().expr(locat_expr)

      # Add to the table
      self.tab_insert(tab, elem.name, index_value, offset_value)

      # Add the expanded channel use (name, index) to a list
      uses.append((elem.name, index_value))

      self.debug('  {}[{}] at {}'.format(elem.name, index_value, offset_value))
    
    return uses

  # Program ============================================

  def walk_program(self, node):
    #[self.decl(x) for x in node.decls]
    [self.defn(x) for x in node.defs]
  
  # Procedure definitions ===============================

  def defn(self, node):
    #[self.decl(x) for x in node.decls]
    self.debug('New channel scope: '+node.name)
    tab = {}
    uses = self.stmt(node.stmt, [], tab)
    self.debug('Channel label table:')
    for x in tab.keys():
      self.debug('  {}: {}'.format(x, ', '.join(['{}'.format(y) for y in tab[x]])))
  
  # Statements ==========================================

  # Statements containing uses of channels

  def stmt_in(self, node, iters, tab):
    self.debug('out channel {}:'.format(node.left.name))
    
    if isinstance(node.left, ast.ElemId):
      node.uses = self.single_channel(tab, node, node.left)
    
    elif isinstance(node.left, ast.ElemSub):
      node.uses = self.subscript_channel(iters, tab, node, node.left)
    
    else:
      assert 0

  def stmt_out(self, node, iters, tab):
    self.debug('in channel {}:'.format(node.left.name))

    if isinstance(node.left, ast.ElemId):
      node.uses = self.single_channel(tab, node, node.left)
    
    elif isinstance(node.left, ast.ElemSub):
      node.uses = self.subscript_channel(iters, tab, node, node.left)
    
    else:
      assert 0

  def stmt_pcall(self, node, iters, tab):
    node.uses = []
    for x in node.args:
      if isinstance(x, ast.ExprSingle):

        if (isinstance(x.elem, ast.ElemId)
            and x.elem.symbol.type == T_CHAN_SINGLE):
          self.debug('single arg channel {}:'.format(x.elem.name))
          node.uses += self.single_channel(tab, node, x.elem)

        elif (isinstance(x.elem, ast.ElemSub)
            and x.elem.symbol.type == T_CHAN_ARRAY):
          self.debug('subscript arg channel {}:'.format(x.elem.name))
          node.uses += self.subscript_channel(iters, tab, node, x.elem)
    
  # Top-level statements where connections are inserted

  def stmt_rep(self, node, iters, tab):
    self.stmt(node.stmt, iters + node.indicies, tab)
  
  def stmt_par(self, node, iters, tab):
    for (i, x) in enumerate(node.stmt):
      self.stmt(x, iters, tab)
 
  # Other statements containing processes

  def stmt_seq(self, node, iters, tab):
    [self.stmt(x, iters, tab) for x in node.stmt]

  def stmt_if(self, node, iters, tab):
    self.stmt(node.thenstmt, iters, tab)
    self.stmt(node.elsestmt, iters, tab)

  def stmt_while(self, node, iters, tab):
    self.stmt(node.stmt, iters, tab)

  def stmt_for(self, node, iters, tab):
    self.stmt(node.stmt, iters, tab)

  # Statements not containing processes or channels uses

  def stmt_ass(self, node, iters, tab):
    pass

  def stmt_alias(self, node, iters, tab):
    pass

  def stmt_skip(self, node, iters, tab):
    pass

  def stmt_return(self, node, iters, tab):
    pass

  # Prohibited statements

  def stmt_on(self, node, iters, tab):
    assert 0

  def stmt_connect(self, node, iters, tab):
    assert 0

