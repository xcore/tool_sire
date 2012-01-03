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
    def __init__(self, name, chanend, connid, index, target):
      self.name = name
      self.chanend = chanend
      self.connid = connid
      self.index = index
      self.target = target

    def __repr__(self):
      return 'connect {}:{} ({}{}) to {}'.format(self.chanend, self.connid, 
          self.name, '[{}]'.format(self.index) if self.index!=None else '', 
          self.target)

  class ConnSlave(object):
    def __init__(self, name, chanend, connid, index, origin):
      self.name = name
      self.chanend = chanend
      self.connid = connid
      self.index = index
      self.origin = origin

    def __repr__(self):
      return 'connect {}:{} ({}{}) from {}'.format(self.chanend, self.connid, 
          self.name, '[{}]'.format(self.index) if self.index!=None else '', 
          self.origin)

  def __init__(self, device):
    self.device = device
    self.d = []
    [self.d.append([]) for x in range(self.device.num_cores())]

  def aggregate(self, chans, tab, scope):
    """
    Iterate over ChanElemSets and aggregate the expanded channels with their
    locations by location into the 'd' array.
    """
    for x in chans:
      for y in x.elems:
        master = tab.lookup_is_master(x.name, y.index, y.location, scope)
        connid = tab.lookup_connid(x.name, y.index, scope)
        if master:
          slave_loc = tab.lookup_slave_location(x.name, y.index, scope)
          self.d[y.location].append(self.ConnMaster(
            x.name, x.chanend, connid, y.index, slave_loc))
        else:
          master_loc = tab.lookup_master_location(x.name, y.index, scope)
          self.d[y.location].append(self.ConnSlave(
            x.name, x.chanend, connid, y.index, master_loc))
 
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
    self.aggregate(node.chans, node.chantab, None)
    self.stmt(node.stmt, node.chantab, None)

  # Boundary statements (which get distributed)

  def stmt_rep(self, node, tab, scope):
    self.aggregate(node.chans, tab, scope)
    self.stmt(node.stmt, tab, scope)

  # New scope
  def stmt_par(self, node, tab, scope):
    [self.aggregate(x, tab, node.scope) for x in node.chans]
    [self.stmt(x, tab, node.scope) for x in node.stmt]
  
  # New scope
  def stmt_server(self, node, tab, scope):
    [self.aggregate(x, tab, node.scope) for x in node.chans]
    self.stmt(node.server, tab, node.scope)
    self.stmt(node.client, tab, node.scope)
  
  def stmt_on(self, node, tab, scope):
    self.aggregate(node.chans, tab, scope)
    self.stmt(node.stmt, tab, scope)

  # Compound statements

  # New scope
  def stmt_seq(self, node, tab, scope):
    [self.stmt(x, tab, node.scope) for x in node.stmt]

  def stmt_if(self, node, tab, scope):
    self.stmt(node.thenstmt, tab, scope)
    self.stmt(node.elsestmt, tab, scope)

  def stmt_while(self, node, tab, scope):
    self.stmt(node.stmt, tab, scope)

  def stmt_for(self, node, tab, scope):
    self.stmt(node.stmt, tab, scope)

  # Statements not containing statements

  def stmt_skip(self, node, tab, scope):
    pass

  def stmt_pcall(self, node, tab, scope):
    pass

  def stmt_ass(self, node, tab, scope):
    pass

  def stmt_in(self, node, tab, scope):
    pass

  def stmt_out(self, node, tab, scope):
    pass

  def stmt_alias(self, node, tab, scope):
    pass

  def stmt_connect(self, node, tab, scope):
    pass
    
  def stmt_assert(self, node, tab, scope):
    pass

  def stmt_return(self, node, tab, scope):
    pass

