#-----------------------------------------------------------------
# ** ATTENTION **
# This code was automatically generated from the file: ast.cfg 
# Do not modify it directly. Modify ast.cfg and run the generator 
# again.
#-----------------------------------------------------------------

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


class NodeVisitor(object):
  def up(self, tag): pass
  def down(self, tag): pass
  def visit_program(self, node): pass
  def visit_decl(self, node): pass
  def visit_def(self, node): pass
  def visit_param(self, node): pass
  def visit_stmt(self, node): pass
  def visit_stmt_seq(self, node): pass
  def visit_stmt_par(self, node): pass
  def visit_stmt_ass(self, node): pass
  def visit_stmt_in(self, node): pass
  def visit_stmt_out(self, node): pass
  def visit_stmt_alias(self, node): pass
  def visit_stmt_connect(self, node): pass
  def visit_stmt_server(self, node): pass
  def visit_stmt_while(self, node): pass
  def visit_stmt_for(self, node): pass
  def visit_stmt_rep(self, node): pass
  def visit_stmt_if(self, node): pass
  def visit_stmt_on(self, node): pass
  def visit_stmt_pcall(self, node): pass
  def visit_stmt_assert(self, node): pass
  def visit_stmt_return(self, node): pass
  def visit_stmt_skip(self, node): pass
  def visit_expr(self, node): pass
  def visit_expr_single(self, node): pass
  def visit_expr_unary(self, node): pass
  def visit_expr_binop(self, node): pass
  def visit_elem(self, node): pass
  def visit_elem_id(self, node): pass
  def visit_elem_sub(self, node): pass
  def visit_elem_slice(self, node): pass
  def visit_elem_index_range(self, node): pass
  def visit_elem_group(self, node): pass
  def visit_elem_fcall(self, node): pass
  def visit_elem_number(self, node): pass
  def visit_elem_boolean(self, node): pass
  def visit_elem_string(self, node): pass
  def visit_elem_char(self, node): pass


class Program(Node):
  def __init__(self, decls, defs, coord=None):
    self.decls = decls
    self.defs = defs
    self.coord = coord

  def children(self):
    c = []
    if self.decls is not None: c.extend(self.decls)
    if self.defs is not None: c.extend(self.defs)
    return tuple(c)

  def accept(self, visitor):
    tag = visitor.visit_program(self)
    visitor.down(tag)
    for c in self.children():
      c.accept(visitor)
    visitor.up(tag)

  def __repr__(self):
    s =  'Program('
    s += ')'
    return s


class Decl(Node):
  def __init__(self, name, type, expr, coord=None):
    self.name = name
    self.type = type
    self.expr = expr
    self.coord = coord
    self.symbol = None

  def children(self):
    c = []
    return tuple(c)

  def accept(self, visitor):
    tag = visitor.visit_decl(self)
    visitor.down(tag)
    for c in self.children():
      c.accept(visitor)
    visitor.up(tag)

  def __eq__(self, other):
    return self.name == other.name

  def __hash__(self):
    return self.name.__hash__()

  def __repr__(self):
    s =  'Decl('
    s += ', '.join('%s' % v for v in [self.name, self.type, self.expr])
    s += ')'
    return s


class Def(Node):
  def __init__(self, name, type, formals, decls, stmt, coord=None):
    self.name = name
    self.type = type
    self.formals = formals
    self.decls = decls
    self.stmt = stmt
    self.coord = coord
    self.symbol = None

  def children(self):
    c = []
    if self.stmt is not None: c.append(self.stmt)
    if self.formals is not None: c.extend(self.formals)
    if self.decls is not None: c.extend(self.decls)
    return tuple(c)

  def accept(self, visitor):
    tag = visitor.visit_def(self)
    visitor.down(tag)
    for c in self.children():
      c.accept(visitor)
    visitor.up(tag)

  def __eq__(self, other):
    return self.name == other.name

  def __hash__(self):
    return self.name.__hash__()

  def __repr__(self):
    s =  'Def('
    s += ', '.join('%s' % v for v in [self.name, self.type])
    s += ')'
    return s


class Param(Node):
  def __init__(self, name, type, expr, coord=None):
    self.name = name
    self.type = type
    self.expr = expr
    self.coord = coord
    self.symbol = None

  def children(self):
    c = []
    return tuple(c)

  def accept(self, visitor):
    tag = visitor.visit_param(self)
    visitor.down(tag)
    for c in self.children():
      c.accept(visitor)
    visitor.up(tag)

  def __eq__(self, other):
    return self.name == other.name

  def __hash__(self):
    return self.name.__hash__()

  def __repr__(self):
    s =  'Param('
    s += ', '.join('%s' % v for v in [self.name, self.type, self.expr])
    s += ')'
    return s


class Stmt(Node):
  def __init__(self, coord=None):
    self.coord = coord

  def children(self):
    return ()

  def accept(self, visitor):
    tag = visitor.visit_stmt(self)
    visitor.down(tag)
    visitor.up(tag)

  def __repr__(self):
    s =  'Stmt('
    s += ')'
    return s


class StmtSeq(Stmt):
  def __init__(self, stmt, coord=None):
    self.stmt = stmt
    self.coord = coord

  def children(self):
    c = []
    if self.stmt is not None: c.extend(self.stmt)
    return tuple(c)

  def accept(self, visitor):
    tag = visitor.visit_stmt_seq(self)
    visitor.down(tag)
    for c in self.children():
      c.accept(visitor)
    visitor.up(tag)

  def __repr__(self):
    s =  'StmtSeq('
    s += ')'
    return s


class StmtPar(Stmt):
  def __init__(self, stmt, coord=None):
    self.stmt = stmt
    self.coord = coord

  def children(self):
    c = []
    if self.stmt is not None: c.extend(self.stmt)
    return tuple(c)

  def accept(self, visitor):
    tag = visitor.visit_stmt_par(self)
    visitor.down(tag)
    for c in self.children():
      c.accept(visitor)
    visitor.up(tag)

  def __repr__(self):
    s =  'StmtPar('
    s += ')'
    return s


class StmtAss(Stmt):
  def __init__(self, left, expr, coord=None):
    self.left = left
    self.expr = expr
    self.coord = coord

  def children(self):
    c = []
    if self.left is not None: c.append(self.left)
    if self.expr is not None: c.append(self.expr)
    return tuple(c)

  def accept(self, visitor):
    tag = visitor.visit_stmt_ass(self)
    visitor.down(tag)
    for c in self.children():
      c.accept(visitor)
    visitor.up(tag)

  def __repr__(self):
    s =  'StmtAss('
    s += ')'
    return s


class StmtIn(Stmt):
  def __init__(self, left, expr, coord=None):
    self.left = left
    self.expr = expr
    self.coord = coord

  def children(self):
    c = []
    if self.left is not None: c.append(self.left)
    if self.expr is not None: c.append(self.expr)
    return tuple(c)

  def accept(self, visitor):
    tag = visitor.visit_stmt_in(self)
    visitor.down(tag)
    for c in self.children():
      c.accept(visitor)
    visitor.up(tag)

  def __repr__(self):
    s =  'StmtIn('
    s += ')'
    return s


class StmtOut(Stmt):
  def __init__(self, left, expr, coord=None):
    self.left = left
    self.expr = expr
    self.coord = coord

  def children(self):
    c = []
    if self.left is not None: c.append(self.left)
    if self.expr is not None: c.append(self.expr)
    return tuple(c)

  def accept(self, visitor):
    tag = visitor.visit_stmt_out(self)
    visitor.down(tag)
    for c in self.children():
      c.accept(visitor)
    visitor.up(tag)

  def __repr__(self):
    s =  'StmtOut('
    s += ')'
    return s


class StmtAlias(Stmt):
  def __init__(self, left, slice, coord=None):
    self.left = left
    self.slice = slice
    self.coord = coord

  def children(self):
    c = []
    if self.left is not None: c.append(self.left)
    if self.slice is not None: c.append(self.slice)
    return tuple(c)

  def accept(self, visitor):
    tag = visitor.visit_stmt_alias(self)
    visitor.down(tag)
    for c in self.children():
      c.accept(visitor)
    visitor.up(tag)

  def __repr__(self):
    s =  'StmtAlias('
    s += ')'
    return s


class StmtConnect(Stmt):
  def __init__(self, left, id, expr, master, coord=None):
    self.left = left
    self.id = id
    self.expr = expr
    self.master = master
    self.coord = coord

  def children(self):
    c = []
    if self.left is not None: c.append(self.left)
    if self.id is not None: c.append(self.id)
    if self.expr is not None: c.append(self.expr)
    return tuple(c)

  def accept(self, visitor):
    tag = visitor.visit_stmt_connect(self)
    visitor.down(tag)
    for c in self.children():
      c.accept(visitor)
    visitor.up(tag)

  def __repr__(self):
    s =  'StmtConnect('
    s += ', '.join('%s' % v for v in [self.master])
    s += ')'
    return s


class StmtServer(Stmt):
  def __init__(self, server, slave, coord=None):
    self.server = server
    self.slave = slave
    self.coord = coord

  def children(self):
    c = []
    if self.server is not None: c.append(self.server)
    if self.slave is not None: c.append(self.slave)
    return tuple(c)

  def accept(self, visitor):
    tag = visitor.visit_stmt_server(self)
    visitor.down(tag)
    for c in self.children():
      c.accept(visitor)
    visitor.up(tag)

  def __repr__(self):
    s =  'StmtServer('
    s += ')'
    return s


class StmtWhile(Stmt):
  def __init__(self, cond, stmt, coord=None):
    self.cond = cond
    self.stmt = stmt
    self.coord = coord

  def children(self):
    c = []
    if self.cond is not None: c.append(self.cond)
    if self.stmt is not None: c.append(self.stmt)
    return tuple(c)

  def accept(self, visitor):
    tag = visitor.visit_stmt_while(self)
    visitor.down(tag)
    for c in self.children():
      c.accept(visitor)
    visitor.up(tag)

  def __repr__(self):
    s =  'StmtWhile('
    s += ')'
    return s


class StmtFor(Stmt):
  def __init__(self, index, stmt, coord=None):
    self.index = index
    self.stmt = stmt
    self.coord = coord

  def children(self):
    c = []
    if self.index is not None: c.append(self.index)
    if self.stmt is not None: c.append(self.stmt)
    return tuple(c)

  def accept(self, visitor):
    tag = visitor.visit_stmt_for(self)
    visitor.down(tag)
    for c in self.children():
      c.accept(visitor)
    visitor.up(tag)

  def __repr__(self):
    s =  'StmtFor('
    s += ')'
    return s


class StmtRep(Stmt):
  def __init__(self, indicies, stmt, coord=None):
    self.indicies = indicies
    self.stmt = stmt
    self.coord = coord

  def children(self):
    c = []
    if self.stmt is not None: c.append(self.stmt)
    if self.indicies is not None: c.extend(self.indicies)
    return tuple(c)

  def accept(self, visitor):
    tag = visitor.visit_stmt_rep(self)
    visitor.down(tag)
    for c in self.children():
      c.accept(visitor)
    visitor.up(tag)

  def __repr__(self):
    s =  'StmtRep('
    s += ')'
    return s


class StmtIf(Stmt):
  def __init__(self, cond, thenstmt, elsestmt, coord=None):
    self.cond = cond
    self.thenstmt = thenstmt
    self.elsestmt = elsestmt
    self.coord = coord

  def children(self):
    c = []
    if self.cond is not None: c.append(self.cond)
    if self.thenstmt is not None: c.append(self.thenstmt)
    if self.elsestmt is not None: c.append(self.elsestmt)
    return tuple(c)

  def accept(self, visitor):
    tag = visitor.visit_stmt_if(self)
    visitor.down(tag)
    for c in self.children():
      c.accept(visitor)
    visitor.up(tag)

  def __repr__(self):
    s =  'StmtIf('
    s += ')'
    return s


class StmtOn(Stmt):
  def __init__(self, expr, stmt, coord=None):
    self.expr = expr
    self.stmt = stmt
    self.coord = coord

  def children(self):
    c = []
    if self.expr is not None: c.append(self.expr)
    if self.stmt is not None: c.append(self.stmt)
    return tuple(c)

  def accept(self, visitor):
    tag = visitor.visit_stmt_on(self)
    visitor.down(tag)
    for c in self.children():
      c.accept(visitor)
    visitor.up(tag)

  def __repr__(self):
    s =  'StmtOn('
    s += ')'
    return s


class StmtPcall(Stmt):
  def __init__(self, name, args, coord=None):
    self.name = name
    self.args = args
    self.coord = coord
    self.symbol = None

  def children(self):
    c = []
    if self.args is not None: c.extend(self.args)
    return tuple(c)

  def accept(self, visitor):
    tag = visitor.visit_stmt_pcall(self)
    visitor.down(tag)
    for c in self.children():
      c.accept(visitor)
    visitor.up(tag)

  def __eq__(self, other):
    return self.name == other.name

  def __hash__(self):
    return self.name.__hash__()

  def __repr__(self):
    s =  'StmtPcall('
    s += ', '.join('%s' % v for v in [self.name])
    s += ')'
    return s


class StmtAssert(Stmt):
  def __init__(self, expr, coord=None):
    self.expr = expr
    self.coord = coord

  def children(self):
    c = []
    if self.expr is not None: c.append(self.expr)
    return tuple(c)

  def accept(self, visitor):
    tag = visitor.visit_stmt_assert(self)
    visitor.down(tag)
    for c in self.children():
      c.accept(visitor)
    visitor.up(tag)

  def __repr__(self):
    s =  'StmtAssert('
    s += ')'
    return s


class StmtReturn(Stmt):
  def __init__(self, expr, coord=None):
    self.expr = expr
    self.coord = coord

  def children(self):
    c = []
    if self.expr is not None: c.append(self.expr)
    return tuple(c)

  def accept(self, visitor):
    tag = visitor.visit_stmt_return(self)
    visitor.down(tag)
    for c in self.children():
      c.accept(visitor)
    visitor.up(tag)

  def __repr__(self):
    s =  'StmtReturn('
    s += ')'
    return s


class StmtSkip(Stmt):
  def __init__(self, coord=None):
    self.coord = coord

  def children(self):
    return ()

  def accept(self, visitor):
    tag = visitor.visit_stmt_skip(self)
    visitor.down(tag)
    visitor.up(tag)

  def __repr__(self):
    s =  'StmtSkip('
    s += ')'
    return s


class Expr(Node):
  def __init__(self, coord=None):
    self.coord = coord

  def children(self):
    return ()

  def accept(self, visitor):
    tag = visitor.visit_expr(self)
    visitor.down(tag)
    visitor.up(tag)

  def __repr__(self):
    s =  'Expr('
    s += ')'
    return s


class ExprSingle(Expr):
  def __init__(self, elem, coord=None):
    self.elem = elem
    self.coord = coord

  def children(self):
    c = []
    if self.elem is not None: c.append(self.elem)
    return tuple(c)

  def accept(self, visitor):
    tag = visitor.visit_expr_single(self)
    visitor.down(tag)
    for c in self.children():
      c.accept(visitor)
    visitor.up(tag)

  def __repr__(self):
    s =  'ExprSingle('
    s += ')'
    return s


class ExprUnary(Expr):
  def __init__(self, op, elem, coord=None):
    self.op = op
    self.elem = elem
    self.coord = coord

  def children(self):
    c = []
    if self.elem is not None: c.append(self.elem)
    return tuple(c)

  def accept(self, visitor):
    tag = visitor.visit_expr_unary(self)
    visitor.down(tag)
    for c in self.children():
      c.accept(visitor)
    visitor.up(tag)

  def __repr__(self):
    s =  'ExprUnary('
    s += ', '.join('%s' % v for v in [self.op])
    s += ')'
    return s


class ExprBinop(Expr):
  def __init__(self, op, elem, right, coord=None):
    self.op = op
    self.elem = elem
    self.right = right
    self.coord = coord

  def children(self):
    c = []
    if self.elem is not None: c.append(self.elem)
    if self.right is not None: c.append(self.right)
    return tuple(c)

  def accept(self, visitor):
    tag = visitor.visit_expr_binop(self)
    visitor.down(tag)
    for c in self.children():
      c.accept(visitor)
    visitor.up(tag)

  def __repr__(self):
    s =  'ExprBinop('
    s += ', '.join('%s' % v for v in [self.op])
    s += ')'
    return s


class Elem(Node):
  def __init__(self, coord=None):
    self.coord = coord

  def children(self):
    return ()

  def accept(self, visitor):
    tag = visitor.visit_elem(self)
    visitor.down(tag)
    visitor.up(tag)

  def __repr__(self):
    s =  'Elem('
    s += ')'
    return s


class ElemId(Elem):
  def __init__(self, name, coord=None):
    self.name = name
    self.coord = coord
    self.symbol = None

  def children(self):
    c = []
    return tuple(c)

  def accept(self, visitor):
    tag = visitor.visit_elem_id(self)
    visitor.down(tag)
    for c in self.children():
      c.accept(visitor)
    visitor.up(tag)

  def __eq__(self, other):
    return self.name == other.name

  def __hash__(self):
    return self.name.__hash__()

  def __repr__(self):
    s =  'ElemId('
    s += ', '.join('%s' % v for v in [self.name])
    s += ')'
    return s


class ElemSub(Elem):
  def __init__(self, name, expr, coord=None):
    self.name = name
    self.expr = expr
    self.coord = coord
    self.symbol = None

  def children(self):
    c = []
    if self.expr is not None: c.append(self.expr)
    return tuple(c)

  def accept(self, visitor):
    tag = visitor.visit_elem_sub(self)
    visitor.down(tag)
    for c in self.children():
      c.accept(visitor)
    visitor.up(tag)

  def __eq__(self, other):
    return self.name == other.name

  def __hash__(self):
    return self.name.__hash__()

  def __repr__(self):
    s =  'ElemSub('
    s += ', '.join('%s' % v for v in [self.name])
    s += ')'
    return s


class ElemSlice(Elem):
  def __init__(self, name, base, count, coord=None):
    self.name = name
    self.base = base
    self.count = count
    self.coord = coord
    self.symbol = None

  def children(self):
    c = []
    if self.base is not None: c.append(self.base)
    if self.count is not None: c.append(self.count)
    return tuple(c)

  def accept(self, visitor):
    tag = visitor.visit_elem_slice(self)
    visitor.down(tag)
    for c in self.children():
      c.accept(visitor)
    visitor.up(tag)

  def __eq__(self, other):
    return self.name == other.name

  def __hash__(self):
    return self.name.__hash__()

  def __repr__(self):
    s =  'ElemSlice('
    s += ', '.join('%s' % v for v in [self.name])
    s += ')'
    return s


class ElemIndexRange(Elem):
  def __init__(self, name, base, count, coord=None):
    self.name = name
    self.base = base
    self.count = count
    self.coord = coord
    self.symbol = None

  def children(self):
    c = []
    if self.base is not None: c.append(self.base)
    if self.count is not None: c.append(self.count)
    return tuple(c)

  def accept(self, visitor):
    tag = visitor.visit_elem_index_range(self)
    visitor.down(tag)
    for c in self.children():
      c.accept(visitor)
    visitor.up(tag)

  def __eq__(self, other):
    return self.name == other.name

  def __hash__(self):
    return self.name.__hash__()

  def __repr__(self):
    s =  'ElemIndexRange('
    s += ', '.join('%s' % v for v in [self.name])
    s += ')'
    return s


class ElemGroup(Elem):
  def __init__(self, expr, coord=None):
    self.expr = expr
    self.coord = coord

  def children(self):
    c = []
    if self.expr is not None: c.append(self.expr)
    return tuple(c)

  def accept(self, visitor):
    tag = visitor.visit_elem_group(self)
    visitor.down(tag)
    for c in self.children():
      c.accept(visitor)
    visitor.up(tag)

  def __repr__(self):
    s =  'ElemGroup('
    s += ')'
    return s


class ElemFcall(Elem):
  def __init__(self, name, args, coord=None):
    self.name = name
    self.args = args
    self.coord = coord
    self.symbol = None

  def children(self):
    c = []
    if self.args is not None: c.extend(self.args)
    return tuple(c)

  def accept(self, visitor):
    tag = visitor.visit_elem_fcall(self)
    visitor.down(tag)
    for c in self.children():
      c.accept(visitor)
    visitor.up(tag)

  def __eq__(self, other):
    return self.name == other.name

  def __hash__(self):
    return self.name.__hash__()

  def __repr__(self):
    s =  'ElemFcall('
    s += ', '.join('%s' % v for v in [self.name])
    s += ')'
    return s


class ElemNumber(Elem):
  def __init__(self, value, coord=None):
    self.value = value
    self.coord = coord

  def children(self):
    c = []
    return tuple(c)

  def accept(self, visitor):
    tag = visitor.visit_elem_number(self)
    visitor.down(tag)
    for c in self.children():
      c.accept(visitor)
    visitor.up(tag)

  def __repr__(self):
    s =  'ElemNumber('
    s += ', '.join('%s' % v for v in [self.value])
    s += ')'
    return s


class ElemBoolean(Elem):
  def __init__(self, value, coord=None):
    self.value = value
    self.coord = coord

  def children(self):
    c = []
    return tuple(c)

  def accept(self, visitor):
    tag = visitor.visit_elem_boolean(self)
    visitor.down(tag)
    for c in self.children():
      c.accept(visitor)
    visitor.up(tag)

  def __repr__(self):
    s =  'ElemBoolean('
    s += ', '.join('%s' % v for v in [self.value])
    s += ')'
    return s


class ElemString(Elem):
  def __init__(self, value, coord=None):
    self.value = value
    self.coord = coord

  def children(self):
    c = []
    return tuple(c)

  def accept(self, visitor):
    tag = visitor.visit_elem_string(self)
    visitor.down(tag)
    for c in self.children():
      c.accept(visitor)
    visitor.up(tag)

  def __repr__(self):
    s =  'ElemString('
    s += ', '.join('%s' % v for v in [self.value])
    s += ')'
    return s


class ElemChar(Elem):
  def __init__(self, value, coord=None):
    self.value = value
    self.coord = coord

  def children(self):
    c = []
    return tuple(c)

  def accept(self, visitor):
    tag = visitor.visit_elem_char(self)
    visitor.down(tag)
    for c in self.children():
      c.accept(visitor)
    visitor.up(tag)

  def __repr__(self):
    s =  'ElemChar('
    s += ', '.join('%s' % v for v in [self.value])
    s += ')'
    return s


