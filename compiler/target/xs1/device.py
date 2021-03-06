# Copyright (c) 2011, James Hanlon, All rights reserved
# This software is freely distributable under a derivative of the
# University of Illinois/NCSA Open Source License posted in
# LICENSE.txt and at <http://github.xcore.com/>

from target.definitions import *
from target.device import Device
from error import Error

class XS1Device(Device):
  def __init__(self, type, name, num_nodes, num_cores_per_node):
    super(XS1Device, self).__init__(SYSTEM_TYPE_XS1, type, name, num_nodes)
    self.num_cores_per_node = num_cores_per_node

  def num_cores(self):
    return self.num_nodes * self.num_cores_per_node

  def source_file_ext(self):
    return XS1_SOURCE_FILE_EXT

  def assembly_file_ext(self):
    return XS1_ASSEMBLY_FILE_EXT

  def binary_file_ext(self):
    return XS1_BINARY_FILE_EXT


AVAILABLE_XS1_DEVICES = [
  
  # XS1-G
  XS1Device(XS1_DEVICE_TYPE_G, 'XMP-1',  1,  1),
  XS1Device(XS1_DEVICE_TYPE_G, 'XMP-4',  1,  4),
  XS1Device(XS1_DEVICE_TYPE_G, 'XMP-16', 4,  4),
  XS1Device(XS1_DEVICE_TYPE_G, 'XMP-32', 8,  4),
  XS1Device(XS1_DEVICE_TYPE_G, 'XMP-64', 16, 4),
  
  # XS1-L
  XS1Device(XS1_DEVICE_TYPE_L, 'XS1-L8A',   8,   1),
  XS1Device(XS1_DEVICE_TYPE_L, 'XS1-L128A', 128, 1),
  XS1Device(XS1_DEVICE_TYPE_L, 'XS1-L256A', 256, 1),
  XS1Device(XS1_DEVICE_TYPE_L, 'XS1-L512A', 512, 1),
]

def get_xs1_device(num_cores):
  return XS1Device(XS1_DEVICE_TYPE_L, 'XS1-L{}A'.format(num_cores), 1, num_cores)
  #d = [x for x in AVAILABLE_XS1_DEVICES if num_cores==x.num_cores()]
  #if len(d) > 0:
  #  return d[0]
  #else:
  #  raise Error('invalid XS1 target ({} cores)'.format(num_cores))

