#!/usr/bin/env python3

# Copyright (c) 2011, James Hanlon, All rights reserved
# This software is freely distributable under a derivative of the
# University of Illinois/NCSA Open Source License posted in
# LICENSE.txt and at <http://github.xcore.com/>

#-----------------------------------------------------------------
# Generate ast module from a specification
#
# Based on pycparser by Eli Bendersky and astgen.py from the
# Python 2.5 code-base.
#-----------------------------------------------------------------

from string import Template
import util

class ASTGenerator(object):
    def __init__(self, cfg_filename='ast.cfg'):
        """ Initialize the code generator from a configuration file.
        """
        self.cfg_filename = cfg_filename
        self.node_cfg = [NodeCfg(name, contents) for (name, contents) in self.parse_cfgfile(cfg_filename)]

    def generate(self, file=None):
        """ Generates the code into file, an open file buffer.
        """
        src = Template(_PROLOGUE_COMMENT).substitute(
            cfg_filename=self.cfg_filename)
        
        src += _PROLOGUE_CODE

        src += self.gen_visitor()

        for node_cfg in self.node_cfg:
            src += node_cfg.gen_source() + '\n\n'
        
        file.write(src)

    def parse_cfgfile(self, filename):
        """ Parse the configuration file and yield pairs of (name, contents) 
            for each node.
        """
        with open(filename, "r") as f:
            for line in f:
                line = line.strip()
                if not line or line.startswith('#'):
                    continue
                colon_i = line.find(':')
                lbracket_i = line.find('[')
                rbracket_i = line.find(']')
                if colon_i < 1 or lbracket_i <= colon_i or rbracket_i <= lbracket_i:
                    raise RuntimeError("Invalid line in %s:\n%s\n" % (filename, line))

                name = line[:colon_i]
                val = line[lbracket_i + 1:rbracket_i]
                vallist = [v.strip() for v in val.split(',')] if val else []
                yield name, vallist

    def gen_visitor(self):
        """ Generate a base visitor class that does nothing
        """
        src = 'class NodeVisitor(object):\n'
        src += '    def up(self, tag): pass\n'
        src += '    def down(self, tag): pass\n'
        for x in self.node_cfg:
            src += '    def visit_'+util.camel_to_under(x.name)+'(self, node): pass\n'

        src += '\n\n'
        return src

class NodeCfg(object):
    """ Node configuration. 
        name: node name
        contents: a list of contents - attributes and child nodes 
    """
    def __init__(self, name, contents):
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
        src = self.gen_init()
        src += '\n' + self.gen_children()
        src += '\n' + self.gen_accept()
        src += '\n' + self.gen_repr()
        return src
    
    def gen_init(self):
        src = "class %s(Node):\n" % self.name

        if self.all_entries:
            args = ', '.join(self.all_entries)
            arglist = '(self, %s, coord=None)' % args
        else:
            arglist = '(self, coord=None)'
        
        src += "    def __init__%s:\n" % arglist
        
        for name in self.all_entries + ['coord']:
            src += "        self.%s = %s\n" % (name, name)
        
        return src
    
    def gen_children(self):
        src = '    def children(self):\n'
        
        if self.all_entries:
            src += '        c = []\n'
            
            template = ('' +
                '        if self.%s is not None:' +
                ' c.%s(self.%s)\n')
            
            for child in self.child:
                src += template % (child, 'append', child)
            
            for seq_child in self.seq_child:
                src += template % (seq_child, 'extend', seq_child)
                    
            src += '        return tuple(c)\n'
        else:
            src += '        return ()\n'
            
        return src

    def gen_accept(self):
        src =  '    def accept(self, visitor):\n'
        src += '        tag = visitor.visit_{}(self)\n'.format(
                (util.camel_to_under(self.name)))
        src += '        visitor.down(tag)\n'
        if self.all_entries:
            src += "        for c in self.children():\n"
            src += "            c.accept(visitor)\n"
        src += '        visitor.up(tag)\n'
        return src

    def gen_repr(self):
        src =  '    def __repr__(self):\n'
        src += "        s =  '{}('".format(self.name)+'\n'
        if self.attr:
            src += "        s += ', '.join('%s' % v for v in ["
            src += ', '.join('self.%s' % v for v in self.attr)
            src += "])\n"
        src += "        s += ')'\n"
        #src += "        s += ' at {}'.format(self.coord)\n"
        src += '        return s'
        return src

_PROLOGUE_COMMENT = \
r'''#-----------------------------------------------------------------
# ** ATTENTION **
# This code was automatically generated from the file:
# $cfg_filename 
#
# Do not modify it directly. Modify the configuration file and
# run the generator again.
#-----------------------------------------------------------------
'''

_PROLOGUE_CODE = r'''
import sys

class Node(object):
    """ Abstract base class for AST nodes.
    """
    def children(self):
        """ A sequence of all children that are Nodes
        """
        pass

    def accept(self, visitor):
        """ Accept a visitor
        """
        pass


'''

if __name__ == "__main__":
    import sys
    ast_gen = ASTGenerator('ast.cfg')
    ast_gen.generate(open('ast.py', 'w'))

