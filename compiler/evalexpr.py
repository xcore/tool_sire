# Copyright (c) 2011, James Hanlon, All rights reserved
# This software is freely distributable under a derivative of the
# University of Illinois/NCSA Open Source License posted in
# LICENSE.txt and at <http://github.xcore.com/>

import error
import ast
from walker import NodeWalker

class EvaluateExpr(NodeWalker):
  """
  Evaluate a constant-valued expression.
  """
  def __init__(self):
    pass

  # Expressions =========================================

  def expr_single(self, node):
    return self.elem(node.elem)

  def expr_unary(self, node):
    a = self.elem(node.elem)
    
    if not a:
      return None

    if node.op == '-':
      return -a
    elif node.op == '~':
      return ~a
    else:
      assert 0

  def expr_binop(self, node):
    a = self.elem(node.elem)
    b = self.expr(node.right)
  
    if not (a and b):
      return None
    
    if node.op == '+':
      return a + b
    elif node.op == '-':
      return a - b 
    elif node.op == '*':
      return a * b
    elif node.op == '/':
      return a / b
    elif node.op == '%':
      return a % b
    elif node.op == 'or':
      return a | b
    elif node.op == 'and':
      return a & b
    elif node.op == 'xor':
      return a ^ b
    elif node.op == '<<':
      return a << b
    elif node.op == '>>':
      return a >> b
    elif node.op == '<':
      return a < b
    elif node.op == '>':
      return a > b
    elif node.op == '<=':
      return a <= b
    elif node.op == '>=':
      return a >= b
    elif node.op == '=':
      return a == b
    elif node.op == '~=':
      return a != b
    else:
      assert 0
  
  # Elements= ===========================================

  def elem_id(self, node):
    #print('eval: id: '+node.name+', {}'.format(node.symbol))
    s = node.symbol
    #if s.value: 
    #  print('Evaluating elem: '+node.name+', {} = {}'.format(s, s.value))
    return s.value if s and s.value else None

  def elem_group(self, node):
    return self.expr(node.expr)

  def elem_number(self, node):
    return node.value

  def elem_boolean(self, node):
    return node.value

  def elem_char(self, node):
    return node.value
  
  # Disallowed
  
  def elem_fcall(self, node):
    return None

  def elem_sub(self, node):
    return None

  def elem_slice(self, node):
    return None

  def elem_index(self, node):
    return None

  def elem_string(self, node):
    return None

