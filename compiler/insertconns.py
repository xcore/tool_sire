# Copyright (c) 2011, James Hanlon, All rights reserved
## This software is freely distributable under a derivative of the
## University of Illinois/NCSA Open Source License posted in
## LICENSE.txt and at <http://github.xcore.com/>

import ast
from walker import NodeWalker
from typedefs import *

from printer import Printer

class InsertConns(NodeWalker):
  """
  Propagate the expanded channel uses up to replicator or composition level and
  insert the corresponding connections. For each connection set (for a single
  channel or subscripted array) allocate a new channel end which is declared in
  the procedure scope.
  """
  def __init__(self, print_debug=True):
    self.print_debug = print_debug

  def debug(self, s):
    if self.print_debug:
      print(s)
  
  def chankey(self, name, index):
    """
    Given a channel name and its index return a key concatenating these.
    """
    return '{}{}'.format(name, '' if index==None else index)

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

  # Program ============================================

  def walk_program(self, node):
    [self.defn(x) for x in node.defs]
  
  # Procedure definitions ===============================

  def defn(self, node):
    self.debug('New channel scope: '+node.name)
    decls = set()
    uses = self.stmt(node.stmt, decls)
    node.stmt = self.insert_connections(node.stmt, uses)

    # Insert any new channel end declarations
    for x in decls:
      pass
  
  # Statements ==========================================

  # Statements containing uses of channels

  def stmt_in(self, node, decls):
    self.debug('out channel {}:'.format(node.left.name))
    return set(node.uses)

  def stmt_out(self, node, decls):
    self.debug('in channel {}:'.format(node.left.name))
    return set(node.uses)

  def stmt_pcall(self, node, decls):
    self.debug('pcall: '.format(node.name))
    return set(node.uses)
    
  # Top-level statements where connections are inserted

  def stmt_rep(self, node, decls):
    uses = self.stmt(node.stmt, decls)
    node.stmt = self.insert_connections(node.stmt, uses)

    # Add channel end declarations

    return set()
  
  def stmt_par(self, node, decls):
    for (i, x) in enumerate(node.stmt):
      uses = self.stmt(x, decls)
      node.stmt[i] = self.insert_connections(node.stmt[i], uses) 
    
    # Add channel end declarations
    
    return set()
 
  # Other statements containing processes

  def stmt_seq(self, node, decls):
    uses = set()
    [uses.update(self.stmt(x, decls)) for x in node.stmt]
    return uses

  def stmt_if(self, node, decls):
    uses = self.stmt(node.thenstmt, decls)
    uses |= self.stmt(node.elsestmt, decls)
    return uses

  def stmt_while(self, node, decls):
    return self.stmt(node.stmt, decls)

  def stmt_for(self, node, decls):
    return self.stmt(node.stmt, decls)

  # Statements not containing processes or channels uses

  def stmt_ass(self, node, decls):
    return set()

  def stmt_alias(self, node, decls):
    return set()

  def stmt_skip(self, node, decls):
    return set()

  def stmt_return(self, node, decls):
    return set()

  # Prohibited statements

  def stmt_on(self, node):
    assert 0

  def stmt_connect(self, node):
    assert 0

