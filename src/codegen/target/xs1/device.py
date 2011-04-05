# Copyright (c) 2011, James Hanlon, All rights reserved
# This software is freely distributable under a derivative of the
# University of Illinois/NCSA Open Source License posted in
# LICENSE.txt and at <http://github.xcore.com/>

class Device(object):
    def __init__(self, num_nodes, num_cores_per_node, name):
        self.num_nodes = num_nodes
        self.num_cores_per_node = num_cores_per_node
        self.name = name

    def num_cores(self):
        return self.num_nodes * self.num_cores_per_node


# TODO: read these in automatically?
AVAILABLE_DEVICES = [
    Device(1,  1, 'XMP-1'),
    Device(2,  1, 'XMP-2'),
    Device(1,  4, 'XMP-4'),
    Device(4,  4, 'XMP-16'),
    Device(8,  4, 'XMP-32'),
    Device(16, 4, 'XMP-64'),
]
    

