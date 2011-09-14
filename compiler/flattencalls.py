# Copyright (c) 2011, James Hanlon, All rights reserved
# This software is freely distributable under a derivative of the
# University of Illinois/NCSA Open Source License posted in
# LICENSE.txt and at <http://github.xcore.com/>

import copy
import ast
from walker import NodeWalker
from type import Type

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
    self.debug = debug

  def update_replacement(self, replacements, name, pcall):
    """
    Given a replacement 'name' with 'pcall', check the list of replacements to
    see whether we can already replace 'pcall' with something.
    Flattened processes are removed from the signature table.
    """
    if self.debug:
      for (n, p) in replacements:
        print('replace {} with {}'.format(n, p.name))
      print('---')
    for (i, (n, p)) in enumerate(replacements):
      if n == pcall.name:
        pcall = p
    replacements.append((name, pcall))
    self.sig.remove(name)

  # Program ============================================

  def walk_program(self, node):
    """
    Build a new list of definitions with new process definitons occuring
    before their use. We don't consider the main process. 
    """
    defs = []
    replacements = []

    # For each definition see if we need to keep it
    for x in node.defs[:-1]:
      if self.defn(x, replacements):
        defs.append(x)

    # Main process
    self.stmt(node.defs[-1].stmt, replacements)
    defs.append(node.defs[-1])

    # Use the new list of definitions
    node.defs = defs
  
  # Procedure definitions ===============================

  def defn(self, node, replace):
    """
    Look for processes with nested calls which have the structure:
  
    Case 1::

      proc ... is
        p(...)
  
    or case 2::

      proc ... is
        { p(...) }
    """
    if(self.debug):
      print('Def: '+node.name)

    # Case 1
    if isinstance(node.stmt, ast.StmtPcall):
      if(self.debug):
        print('Found nested call in '+node.name)
      self.update_replacement(replace, node.name, node.stmt)
      return False
    
    # Case 2
    elif (isinstance(node.stmt, ast.StmtSeq) 
        and len(node.stmt.stmt) == 0
        and isinstance(node.stmt.stmt[0], ast.StmtPcall)):
      if(self.debug):
        print('Found nested (seq) call in '+node.name)
      self.update_replacement(replace, node.name, node.stmt.stmt[0])
      return False

    # Everything else
    elif isinstance(node.stmt, ast.Stmt):
      self.stmt(node.stmt, replace)
      return True
  
  # Statements ==========================================

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

  def stmt_seq(self, node, replace):
    [self.stmt(x, replace) for x in node.stmt]

  def stmt_par(self, node, replace):
    [self.stmt(x, replace) for x in node.stmt]

  def stmt_server(self, node, replace):
    self.stmt(node.server, replace)
    self.stmt(node.client, replace)

  def stmt_if(self, node, replace):
    self.stmt(node.thenstmt, replace)
    self.stmt(node.elsestmt, replace)

  def stmt_while(self, node, replace):
    self.stmt(node.stmt, replace)

  def stmt_for(self, node, replace):
    self.stmt(node.stmt, replace)

  def stmt_rep(self, node, replace):
    self.stmt(node.stmt, replace)

  def stmt_on(self, node, replace):
    self.stmt(node.stmt, replace)
  
  def stmt_ass(self, node, replace):
    pass

  def stmt_in(self, node, replace):
    pass

  def stmt_out(self, node, replace):
    pass

  def stmt_alias(self, node, replace):
    pass

  def stmt_connect(self, node, replace):
    pass

  def stmt_assert(self, node, replace):
    pass

  def stmt_return(self, node, replace):
    pass

  def stmt_skip(self, node, replace):
    pass

