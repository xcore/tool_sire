# Copyright (c) 2011, James Hanlon, All rights reserved
# This software is freely distributable under a derivative of the
# University of Illinois/NCSA Open Source License posted in
# LICENSE.txt and at <http://github.xcore.com/>

class Device(object):
    """ A generic class to represent a target device.
    """
    def __init__(self, system, name, num_nodes):
        self.name = name
        self.system = system
        self.num_nodes = num_nodes

    def num_cores(self):
        return self.num_nodes
    
    def __str__(self):
        return '{} ({}, {} core)'.format(self.name, self.system, self.num_cores())

