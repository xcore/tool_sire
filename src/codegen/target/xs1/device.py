# Copyright (c) 2011, James Hanlon, All rights reserved
# This software is freely distributable under a derivative of the
# University of Illinois/NCSA Open Source License posted in
# LICENSE.txt and at <http://github.xcore.com/>

from codegen.target.device import Device

SOURCE_FILE_EXT = 'xc'
ASSEMBLY_FILE_EXT = 'S'
BINARY_FILE_EXT = 'xe'

AVAILABLE_XS1_DEVICES = [
    XS1Device('XMP-1',  1,  1),
    XS1Device('XMP-4',  1,  4),
    XS1Device('XMP-16', 4,  4),
    XS1Device('XMP-32', 8,  4),
    XS1Device('XMP-64', 16, 4),
]

class XS1Device(Device):
    def __init__(self, name, num_nodes, num_cores_per_node):
        super(XS1Device, self).__init__('xs1', name, num_nodes)
        self.num_cores_per_node = num_cores_per_node

    def num_cores(self):
        return self.num_nodes * self.num_cores_per_node

    def get_source_file_ext(self):
        return SOURCE_FILE_EXT

    def get_assembly_file_ext(self):
        return ASSEMBLY_FILE_EXT

    def get_binary_file_ext(self):
        return BINARY_FILE_EXT

