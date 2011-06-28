# Copyright (c) 2011, James Hanlon, All rights reserved
## This software is freely distributable under a derivative of the
## University of Illinois/NCSA Open Source License posted in
## LICENSE.txt and at <http://github.xcore.com/>

import ast
from walker import NodeWalker
from typedefs import *
#from LabelChans import ChanElem, ChanExpansion

from printer import Printer

class InsertConns(NodeWalker):
  """
  Propagate the expanded channel uses up to replicator or composition level and
  insert the corresponding connections. For each connection set (for a single
  channel or subscripted array) allocate a new channel end which is declared in
  the procedure scope.
  """
  def __init__(self, print_debug=False):
    self.print_debug = print_debug

  def debug(self, s):
    if self.print_debug:
      print(s)
  
  def insert_connections(self, process, uses):
    """
    Insert connections for a process from a list of channel uses (name, index)
    by composing them in sequence, prior to the process. If there are no
    connecitons to be made, just return the process.
    """
    if len(uses) > 0:
      conns = [ast.StmtSkip() for x in uses]
      return ast.StmtSeq(conns + [process])
    else:
      return process

  def display_chans(self, chans):
    for x in chans:
      if x.expr:
        print('  {}[{}]'.format(x.name, Printer().expr(x.expr)))
      else:
        print('  {}'.format(x.name))
      for y in x.elems:
        if y.master:
          print('    connect {} to {}'.format(
            '{}[{}]'.format(x.name, y.index) if x.expr!=None else x.name, '?'))
        else:
          print('    connect {}'.format(
            '{}[{}]'.format(x.name, y.index) if x.expr!=None else x.name, '?'))


  # Program ============================================

  def walk_program(self, node):
    [self.defn(x) for x in node.defs]
  
  # Procedure definitions ===============================

  def defn(self, node):
    self.debug('Inserting connections for: '+node.name)
    decls = set()
    self.stmt(node.stmt, decls)
    #node.stmt = self.insert_connections(node.stmt, uses)

    self.debug('[def connections]:')
    if self.print_debug:
      self.self.display_chans(node.chans)
  
  # Statements ==========================================

  # Top-level statements where connections are inserted

  def stmt_rep(self, node, decls):
    self.debug('[rep connections]:')
    if self.print_debug:
      self.display_chans(node.chans)
    self.stmt(node.stmt, decls)
    #node.stmt = self.insert_connections(node.stmt, uses)

  def stmt_par(self, node, decls):
    self.debug('[par connections]:')
    for x in node.chans:
        self.debug('[par stmt]: ')
        if self.print_debug:
          self.display_chans(x)

    [self.stmt(x, decls) for x in node.stmt]
 
  # Other statements containing processes

  def stmt_seq(self, node, decls):
    [self.stmt(x, decls) for x in node.stmt]

  def stmt_if(self, node, decls):
    self.stmt(node.thenstmt, decls)
    self.stmt(node.elsestmt, decls)

  def stmt_while(self, node, decls):
    self.stmt(node.stmt, decls)

  def stmt_for(self, node, decls):
    self.stmt(node.stmt, decls)

  # Other statements

  def stmt_in(self, node, decls):
    pass

  def stmt_out(self, node, decls):
    pass

  def stmt_pcall(self, node, decls):
    pass
    
  def stmt_ass(self, node, decls):
    pass

  def stmt_alias(self, node, decls):
    pass

  def stmt_skip(self, node, decls):
    pass

  def stmt_return(self, node, decls):
    pass

  # Prohibited statements

  def stmt_on(self, node):
    assert 0

  def stmt_connect(self, node):
    assert 0

