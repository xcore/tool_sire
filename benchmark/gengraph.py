#! /usr/bin/env python

import sys
import struct
import numpy
from apgl.graph import *
from apgl.generator.ErdosRenyiGenerator import ErdosRenyiGenerator

if len(sys.argv) != 2:
  print('Usage {} <num-vertices>'.format(sys.argv[0]))
  sys.exit(1)

# Generate a random graph
p = 0.05
graph = DenseGraph(VertexList(int(sys.argv[1]), 1))
generator = ErdosRenyiGenerator(p)
graph = generator.generate(graph)

numVertices = graph.getNumVertices()
numEdges = graph.getNumEdges()
print("{} vertices {} edges".format(numVertices, numEdges))

# Write packed adjacency list to a binary file
outfile = 'graph'
f = open(outfile, "wb")
try:
  f.write(struct.pack('i', numVertices))
  f.write(struct.pack('i', numEdges))
  index = 0
  # Vertices
  for i in range(numVertices):
    f.write(struct.pack('i', index))
    #print(index)
    index += len(graph.neighbours(i))
  # Edges
  for i in range(numVertices):
    for x in graph.neighbours(i):
      f.write(struct.pack('i', x))
      #print(x)
      index -= 1
  assert index == 0
finally:
  f.close()

