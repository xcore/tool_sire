#!/usr/bin/env python3

# Copyright (c) 2011, James Hanlon, All rights reserved
# This software is freely distributable under a derivative of the
# University of Illinois/NCSA Open Source License posted in
# LICENSE.txt and at <http://github.xcore.com/>

from string import Template
import util

class ASTGenerator(object):
  """
  Generate ast module from a specification

  Based on pycparser by Eli Bendersky and astgen.py from the
  Python 2.5 code-base.
  """
  def __init__(self, cfg_filename='ast.cfg'):
    """ 
    Initialize the code generator from a configuration file.
    """
    self.cfg_filename = cfg_filename
    self.node_cfg = [NodeCfg(parent, name, contents) 
        for (parent, name, contents) in self.parse_cfgfile(cfg_filename)]

  def generate(self, file=None):
    """ 
    Generates the code into file, an open file buffer.
    """
    src = Template(_PROLOGUE_COMMENT).substitute(
      cfg_filename=self.cfg_filename)
    src += _PROLOGUE_CODE
    src += self.gen_visitor()

    for node_cfg in self.node_cfg:
      src += node_cfg.gen_source() + '\n\n'
    
    file.write(src)

  def parse_cfgfile(self, filename):
    """ 
    Parse the configuration file and yield pairs of (name, contents) for
    each node.
    """
    with open(filename, "r") as f:
      for line in f:
        line = line.strip()
        if not line or line.startswith('#'):
          continue

        colon_i = line.find(':')
        period_i = line.find('.')
        lbracket_i = line.find('[')
        rbracket_i = line.find(']')
        if (period_i < 1 or colon_i < 1 or colon_i <= period_i
            or lbracket_i <= colon_i or rbracket_i <= lbracket_i):
          raise RuntimeError("Invalid line in {}:\n{}\n".format(
            filename, line))

        parent = line[:period_i]
        name = line[period_i+1:colon_i]
        val = line[lbracket_i + 1:rbracket_i]
        vallist = [v.strip() for v in val.split(',')] if val else []
        yield parent, name, vallist

  def gen_visitor(self):
    """ 
    Generate a base visitor class that does nothing.
    """
    src = 'class NodeVisitor(object):\n'
    src += '  def up(self, tag): pass\n'
    src += '  def down(self, tag): pass\n'
    for x in self.node_cfg:
      src += '  def visit_'+util.camel_to_under(x.name)+'(self, node): pass\n'
    src += '\n\n'
    return src

class NodeCfg(object):
  """ 
  Node configuration. 
  name: node name
  contents: a list of contents - attributes and child nodes 
  """
  def __init__(self, parent, name, contents):
    self.parent = parent
    self.name = name
    self.all_entries = []
    self.attr = []
    self.child = []
    self.seq_child = []

    for entry in contents:
      clean_entry = entry.rstrip('*')
      self.all_entries.append(clean_entry)
      
      if entry.endswith('**'):
        self.seq_child.append(clean_entry)
      elif entry.endswith('*'):
        self.child.append(clean_entry)
      else:
        self.attr.append(entry)

  def gen_source(self):
    src =  self.gen_init()
    src += self.gen_children()
    src += self.gen_accept()
    src += self.gen_eq()
    src += self.gen_hash()
    src += self.gen_repr()
    return src
  
  def gen_init(self):
    src = "class {}({}):\n".format(self.name, self.parent)

    if self.all_entries:
      args = ', '.join(self.all_entries)
      arglist = '(self, %s, coord=None)' % args
    else:
      arglist = '(self, coord=None)'
    
    src += "  def __init__%s:\n" % arglist
    
    for name in self.all_entries + ['coord']:
      src += "    self.{0} = {0}\n".format(name)
     
    # Nodes containing a 'name' attribute will have an associated symbol
    if 'name' in self.all_entries:
      src += '    self.symbol = None\n'

    return src+'\n'
  
  def gen_children(self):
    src = '  def children(self):\n'
    
    if self.all_entries:
      src += '    c = []\n'
      
      template = ('' +
        '    if self.%s is not None:' +
        ' c.%s(self.%s)\n')
      
      for child in self.child:
        src += template % (child, 'append', child)
      
      for seq_child in self.seq_child:
        src += template % (seq_child, 'extend', seq_child)
          
      src += '    return tuple(c)\n\n'
    else:
      src += '    return ()\n\n'
      
    return src

  def gen_accept(self):
    src =  '  def accept(self, visitor):\n'
    src += '    tag = visitor.visit_{}(self)\n'.format(
        (util.camel_to_under(self.name)))
    src += '    visitor.down(tag)\n'
    if self.all_entries:
      src += "    for c in self.children():\n"
      src += "      c.accept(visitor)\n"
    src += '    visitor.up(tag)\n\n'
    return src

  def gen_copy(self):
    """
    For equality we define an equals method that tests each attribute in
    turn. This will recursively trigger nested node equality methods. (So
    could be quite expensive). 
    """
    src =  '  def __copy__(self):\n'
    src += '    return '+self.name+'(' 
    for (i, name) in enumerate(self.all_entries + ['coord']):
      src += 'self.{}'.format(name)
      src += ', ' if i<len(self.all_entries) else ''
    src += ')\n\n'
    return src

  def gen_eq(self):
    """
    We base equality on identifiers.
    """
    src = ''
    if self.parent=='Elem' and 'name' in self.all_entries:
      src =  '  def __eq__(self, other):\n'
      src += '    return self.name == other.name\n\n'
      #src += '    return (\n' 
      #for (i, name) in enumerate(self.all_entries):
      #  src += '      self.{0} == other.{0}'.format(name)
      #  src += ' and\n' if i<len(self.all_entries)-1 else '\n'
      #src += '    )\n\n'
      #src += '  def __ne__(self, other):\n'
      #src += '    return not self.name == other.name\n\n'
    return src

  def gen_hash(self):
    """
    Classes with a 'name' attribute can be hashed (inclued in a set).
    """
    src = ''
    if 'name' in self.all_entries:
      src += '  def __hash__(self):\n'
      src += '    return self.name.__hash__()\n\n'
    return src

  def gen_repr(self):
    src =  '  def __repr__(self):\n'
    src += "    s =  '{}('".format(self.name)+'\n'
    if self.attr:
      src += "    s += ', '.join('%s' % v for v in ["
      src += ', '.join('self.%s' % v for v in self.attr)
      src += "])\n"
    src += "    s += ')'\n"
    #src += "    s += ' at {}'.format(self.coord)\n"
    src += '    return s\n'
    return src

_PROLOGUE_COMMENT = \
r'''#-----------------------------------------------------------------
# ** ATTENTION **
# This code was automatically generated from the file: $cfg_filename 
# Do not modify it directly. Modify $cfg_filename and run the generator 
# again.
#-----------------------------------------------------------------
'''

_PROLOGUE_CODE = r'''
import sys

class Node(object):
  """ 
  Abstract base class for AST nodes.
  """
  def children(self):
    """ 
    A sequence of all children that are Nodes.
    """
    pass

  def accept(self, visitor):
    """ 
    Accept a visitor.
    """
    pass


'''

if __name__ == "__main__":
  import sys
  ast_gen = ASTGenerator('ast.cfg')
  ast_gen.generate(open('ast.py', 'w'))

