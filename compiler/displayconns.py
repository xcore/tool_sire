# Copyright (c) 2011, James Hanlon, All rights reserved
# This software is freely distributable under a derivative of the
# University of Illinois/NCSA Open Source License posted in
# LICENSE.txt and at <http://github.xcore.com/>

from walker import NodeWalker

class DisplayConns(NodeWalker):
  """
  Display channel connections per-core.
  """
  class ConnMaster(object):
    def __init__(self, name, chanend, index, target):
      self.name = name
      self.chanend = chanend
      self.index = index
      self.target = target

    def __repr__(self):
      return 'connect {} ({}{}) to {}'.format(self.chanend, self.name, 
          '[{}]'.format(self.index) if self.index!=None else '', 
          self.target)

  class ConnSlave(object):
    def __init__(self, name, chanend, index, origin):
      self.name = name
      self.chanend = chanend
      self.index = index
      self.origin = origin

    def __repr__(self):
      return 'connect {} ({}{}) from {}'.format(self.chanend, self.name, 
          '[{}]'.format(self.index) if self.index!=None else '', 
          self.origin)

  def __init__(self, device):
    self.device = device
    self.d = []
    [self.d.append([]) for x in range(self.device.num_cores())]

  def aggregate(self, chans, tab):
    """
    Iterate over ChanElemSets and aggregate the expanded channels with their
    locations by locaiton into the 'd' array.
    """
    for x in chans:
      for y in x.elems:
        master = tab.is_master(x.name, y.index, y.location)
        if master:
          slave_loc = tab.lookup_slave_location(x.name, y.index)
          self.d[y.location].append(self.ConnMaster(
            x.name, x.chanend, y.index, slave_loc))
        else:
          master_loc = tab.lookup_master_location(x.name, y.index)
          self.d[y.location].append(self.ConnSlave(
            x.name, x.chanend, y.index, master_loc))
 
  def display(self):
    for (i, x) in enumerate(self.d):
      print('Core {}:'.format(i))
      #for y in sorted(x, key=lambda x: (x.name, x.index)):
      for y in sorted(x, key=lambda x: x.chanend):
        print('  {}'.format(y))

  def walk_program(self, node):
    [self.defn(x) for x in node.defs]
    self.display()
  
  def defn(self, node):
    self.aggregate(node.chans, node.chantab)
    self.stmt(node.stmt, node.chantab)

  # Boundary statements (which get distributed)

  def stmt_rep(self, node, tab):
    self.aggregate(node.chans, tab)
    self.stmt(node.stmt, tab)

  def stmt_par(self, node, tab):
    [self.aggregate(x, tab) for x in node.chans]
    [self.stmt(x, tab) for x in node.stmt]
  
  def stmt_server(self, node, tab):
    [self.aggregate(x, tab) for x in node.chans]
    self.stmt(node.server, tab)
    self.stmt(node.client, tab)
  
  def stmt_on(self, node, tab):
    self.aggregate(node.chans, tab)
    self.stmt(node.stmt, tab)

  # Compound statements

  def stmt_seq(self, node, tab):
    [self.stmt(x, tab) for x in node.stmt]

  def stmt_if(self, node, tab):
    self.stmt(node.thenstmt, tab)
    self.stmt(node.elsestmt, tab)

  def stmt_while(self, node, tab):
    self.stmt(node.stmt, tab)

  def stmt_for(self, node, tab):
    self.stmt(node.stmt, tab)

  # Statements not containing statements

  def stmt_skip(self, node, tab):
    pass

  def stmt_pcall(self, node, tab):
    pass

  def stmt_ass(self, node, tab):
    pass

  def stmt_in(self, node, tab):
    pass

  def stmt_out(self, node, tab):
    pass

  def stmt_alias(self, node, tab):
    pass

  def stmt_connect(self, node, tab):
    pass
    
  def stmt_assert(self, node, tab):
    pass

  def stmt_return(self, node, tab):
    pass

