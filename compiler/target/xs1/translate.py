# Copyright (c) 2011, James Hanlon, All rights reserved
# This software is freely distributable under a derivative of the
# University of Illinois/NCSA Open Source License posted in
# LICENSE.txt and at <http://github.xcore.com/>

import sys

from typedefs import *
import definitions as defs
import config
import ast
import builtin
from util import read_file
from walker import NodeWalker
from blocker import Blocker
from blocker import INDENT
from target.xs1.on import gen_on
from target.xs1.par import gen_par

op_conversion = {
  '+'   : '+',
  '-'   : '-',
  '*'   : '*',
  '/'   : '/',
  'rem' : '%',
  'or'  : '|',
  'and' : '&',
  'xor' : '^',
  '~'   : '!',
  '<<'  : '<<',
  '>>'  : '>>',
  '<'   : '<',
  '>'   : '>',
  '<='  : '<=',
  '>='  : '>=',
  '='   : '==',
  '~='  : '!=',
}

builtin_conversion = {
  # Printing
  'printchar'  : '_PRINTCHAR',
  'printcharln': '_PRINTCHARLN',
  'printval'   : '_PRINTVAL',
  'printvalln' : '_PRINTVALLN',
  'printhex'   : '_PRINTHEX',
  'printhexln' : '_PRINTHEXLN',
  'printstr'   : '_PRINTSTR',
  'printstrln' : '_PRINTSTRLN',
  'println'    : '_PRINTLN',
  # File IO
  'fopen'      : '_OPEN',
  'fwrite'     : '_WRITE',
  'fread'      : '_READ',
  'fclose'     : '_CLOSE',
  # Channel communication
  'inp'        : '_INP',
  'out'        : '_OUT',
  'inct'       : '_INCT',
  'outct'      : '_OUTCT',
  'chkctend'   : '_CHKCTEND',
  'outctend'   : '_OUTCTEND',
  # Remote memory access
  'rwrite'     : '_RWRITE',
  'rread'      : '_RREAD',
  # Malloc/free
  'memalloc'   : '_memAlloc',
  'memfree'    : '_memFree',
  # Fixed point
  'mul8_24'    : 'mul8_24',
  'div8_24'    : 'div8_24',
  # System
  'procid'     : '_procId',
  'sp'         : '_sp',
  'time'       : '_TIME',
  'crc'        : 'crc',
  'rand'       : 'rand',
  # Experiments
  'memreadtimed' : '_MEM_READ_TIMED',
  'memwritetimed' : '_MEM_WRITE_TIMED',
  'memctrl' : '_memController'
}

class TranslateXS1(NodeWalker):
  """ 
  A walker class to pretty-print the AST in the langauge syntax.
  """
  def __init__(self, sig, child, buf):
    super(TranslateXS1, self).__init__()
    self.sig = sig
    self.child = child
    self.buf = buf
    self.indent = [INDENT]
    self.blocker = Blocker(self, buf)
    self.label_counter = 0
    self.parent = None

  def out(self, s):
    """ 
    Write an indented line.
    """
    self.blocker.insert(s)

  def asm(self, template, outop=None, inops=None, clobber=None):
    """ 
    Write an inline assembly statement.
    """
    self.out('asm("{}"{}{}{}{}{}{});'.format(
      #template.replace('\n', ' ; '),
      template,
      ':' if outop or inops or clobber else '',
      '"=r"('+outop+')' if outop else '', 
      ':' if inops or clobber  else '', 
      ', '.join(['"r"('+x+')' for x in inops]) if inops else '',
      ':'   if clobber else '',
      ', '.join(['"'+x+'"' for x in clobber]) if clobber else ''
      ))

  def comment(self, s):
    """ 
    Write a comment.
    """
    self.out('// '+s)

  def stmt_block(self, stmt, chans):
    """ 
    Decide whether the statement needs a block.
    """
    if not (isinstance(stmt, ast.StmtSeq) 
        or isinstance(stmt, ast.StmtPar)):
      self.blocker.begin()
      self.stmt(stmt, chans)
      self.blocker.end()
    else:
      self.stmt(stmt, chans)
    
  def procedure_name(self, name):
    """ 
    If a procedure name has a conversion, return it.
    """
    return builtin_conversion[name] if name in builtin_conversion else name

  def arguments(self, args):
    """ 
    Build the list of arguments for a procedure call. If there is an array
    reference proper, either directly or as a slice, it must be loaded
    manually with an assembly inline which forces the compiler to reveal the
    address.
    """
    new = []

    for x in args:
      arg = None

      # Single-element expressions
      if isinstance(x, ast.ExprSingle):
       
        # Whole arrays
        if isinstance(x.elem, ast.ElemId):
          if x.elem.symbol.type == T_VAR_ARRAY:
            tmp = self.blocker.get_tmp()
            self.asm('mov %0, %1', outop=tmp,
                inops=[x.elem.name])
            arg = tmp
        
        # Array slices: either create or use a reference
        elif isinstance(x.elem, ast.ElemSlice):
          if x.elem.symbol.type == T_VAR_ARRAY:
            tmp = self.blocker.get_tmp()
            self.asm('add %0, %1, %2', outop=tmp,
                inops=[x.elem.name, '({})*{}'.format(
                self.expr(x.elem.begin), defs.BYTES_PER_WORD)])
            arg = tmp
          elif x.elem.symbol.type == T_REF_ARRAY:
            arg = '{}+(({})*{})'.format(
                x.elem.name, self.expr(x.elem.base),
                defs.BYTES_PER_WORD)

      new.append(self.expr(x) if not arg else arg)

    return ', '.join(new)

  def get_label(self):
    """
    Get the next unique label.
    """
    l = '_L{}'.format(self.label_counter)
    self.label_counter += 1
    return l

  def header(self):
    self.out('#include <xs1.h>')
    self.out('#include <print.h>')
    self.out('#include <syscall.h>')
    self.out('#include "device.h"')
    self.out('#include "system/definitions.h"')
    self.out('#include "system/xs1/definitions.h"')
    self.out('#include "runtime/xs1/globals.h"')
    self.out('#include "runtime/xs1/source.h"')
    self.out('#include "runtime/xs1/connect.h"')
    self.out('#include "runtime/xs1/pointer.h"')
    self.out('#include "runtime/xs1/system.h"')
    self.out('#include "runtime/xs1/util.h"')
    self.out('')
  
  def jumptable(self, names):
    self.out('/*')
    self.out(' * Jump table')
    self.out(' * ==========')
    self.out(' *')
    [self.out(' * cp[{}] {}'.format(i, x)) for (i, x) in enumerate(names)]
    self.out('*/\n')

  def builtins(self):
    """ 
    Insert builtin code. We include builtin code directly here so that it
    can be transformed in the build process to be made 'mobile'. This is in
    contrast with the MPI implementation where there is only a single
    binary.
    """
    self.out(read_file(config.XS1_SYSTEM_PATH+'/builtins_fixedpoint.xc'))
    self.out(read_file(config.XS1_SYSTEM_PATH+'/builtins_printing.xc'))
    self.out(read_file(config.XS1_SYSTEM_PATH+'/builtins_fileio.xc'))
    self.out(read_file(config.XS1_SYSTEM_PATH+'/builtins_comm.xc'))
    self.out(read_file(config.XS1_SYSTEM_PATH+'/builtins_remotemem.xc'))
    self.out(read_file(config.XS1_SYSTEM_PATH+'/builtins_system.xc'))
    self.out(read_file(config.XS1_SYSTEM_PATH+'/builtins_experiment.xc'))
 
  # Program ============================================

  def walk_program(self, node):

    # List of names for the jump table
    names = builtin.runtime_functions + self.sig.mobile_proc_names

    # Walk the entire program
    self.header()
    self.jumptable(names)
    self.builtins()
    
    # Declarations
    [self.out(self.decl(x, {})) for x in node.decls]
    if len(node.decls) > 0:
      self.out('')
  
    # Prototypes and definitions
    [self.prototype(p) for p in node.defs]
    self.out('')
    [self.definition(p, names) for p in node.defs]

    # Output the buffered blocks
    self.blocker.output()
  
  # Variable declarations ===============================

  def var_decl(self, node, chans):
    if node.type == T_VAR_ARRAY:
      return 'int {}[{}];'.format(node.name, self.expr(node.expr))
    elif node.type == T_REF_ARRAY:
      return 'unsigned '+node.name+';'
    elif node.type == T_VAR_SINGLE:
      return 'int '+node.name+';'
    elif node.type == T_VAL_SINGLE:
      return '#define {} ({})'.format(node.name, self.expr(node.expr))
    elif node.type == T_CHANEND_SINGLE:
      chans[node.name] = defs.CONNECT_MASTER
      return 'unsigned '+node.name+';'
    elif node.type == T_CHANEND_SERVER_SINGLE:
      chans[node.name] = defs.CONNECT_SERVER
      return 'unsigned '+node.name+';'
    elif node.type == T_CHANEND_CLIENT_SINGLE:
      chans[node.name] = defs.CONNECT_CLIENT
      return 'unsigned '+node.name+';'
    else:
      assert 0

  # Procedure definitions ===============================

  def prototype(self, node):
    s = ''
    s += 'void' if node.type == T_PROC else 'int'
    s += ' {}({});'.format(self.procedure_name(node.name),
        ', '.join([self.param(x) for x in node.formals]))
    self.out(s)

  def definition(self, node, names):
    self.out('// cp[{}]'.format(names.index(node.name)))
    self.out('#pragma unsafe arrays')
    s = 'void' if node.type == T_PROC else 'int'
    s += ' {}({}){}'.format(self.procedure_name(node.name),
        ', '.join([self.param(x) for x in node.formals]),
        ';' if not node.stmt else '')
    self.parent = node.name
    self.out(s)
    
    if node.stmt:
      chans = {}
      self.blocker.begin()
      self.stmt_block(node.stmt, chans)
      self.blocker.end()
    
    self.out('')
  
  # Formals =============================================
  
  def param(self, node):
    if node.type == T_VAL_SINGLE:
      return 'int '+node.name
    elif node.type == T_REF_SINGLE:
      return 'int &'+node.name
    elif node.type == T_REF_ARRAY:
      return 'unsigned '+node.name
    elif node.type == T_CHANEND_SINGLE:
      return 'unsigned &'+node.name
    elif node.type == T_CHANEND_SERVER_SINGLE:
      return 'unsigned &'+node.name
    elif node.type == T_CHANEND_CLIENT_SINGLE:
      return 'unsigned &'+node.name
    else:
      assert 0

  # Statements ==========================================
  # These output themselves and pass a map of chanend names to connection
  # type (master, slave, server or client). This map is updated by connect
  # statements which determine the type. This map is used by input and output
  # statments to choose the correct operation.

  def stmt_seq(self, node, chans):
    self.blocker.begin()
    [self.out(self.decl(x, chans)) for x in node.decls]
    for x in node.children(): 
      self.stmt(x, chans)
    self.blocker.end()

  def stmt_par(self, node, chans):
    self.blocker.begin()
    [self.out(self.decl(x, chans)) for x in node.decls]
    gen_par(self, node, chans)
    self.blocker.end()

  def stmt_ass(self, node, chans):
  
    # If the target is an array reference, then generate a store after
    if node.left.symbol.type == T_REF_ARRAY:
      tmp = self.blocker.get_tmp()
      self.out('{} = {};'.format(tmp, self.expr(node.expr)))
      self.asm('stw %0, %1[%2]', 
          inops=[tmp, node.left.name, self.expr(node.left.expr)])
    
    # Otherwise, proceede normally
    else:
      self.out('{} = {};'.format(
        self.elem(node.left), self.expr(node.expr)))

  def stmt_out(self, node, chans):
    left = self.elem(node.left)
    expr = self.expr(node.expr) 
    if chans[node.left.name] == defs.CONNECT_SERVER:
      self.out('SERVER_OUT({}, {});'.format(left, expr))
    elif chans[node.left.name] == defs.CONNECT_CLIENT:
      self.out('CLIENT_OUT({}, {});'.format(left, expr))
    else:
      self.out('OUT({}, {});'.format(left, expr))

  def stmt_in(self, node, chans):
    left = self.elem(node.left)
    expr = self.expr(node.expr) 
    if chans[node.left.name] == defs.CONNECT_SERVER:
      self.out('SERVER_IN({}, {});'.format(left, expr))
    elif chans[node.left.name] == defs.CONNECT_CLIENT:
      self.out('CLIENT_IN({}, {});'.format(left, expr))
    else:
      self.out('IN({}, {});'.format(left, expr))
    
  def stmt_out_tag(self, node, chans):
    left = self.elem(node.left)
    expr = self.expr(node.expr) 
    if chans[node.left.name] == defs.CONNECT_SERVER:
      self.out('SERVER_OUT_TAG({}, {});'.format(left, expr))
    elif chans[node.left.name] == defs.CONNECT_CLIENT:
      self.out('CLIENT_OUT_TAG({}, {});'.format(left, expr))
    else:
      self.out('OUT({}, {});'.format(left, expr))

  def stmt_in_tag(self, node, chans):
    left = self.elem(node.left)
    expr = self.expr(node.expr) 
    if chans[node.left.name] == defs.CONNECT_SERVER:
      self.out('SERVER_IN_TAG({}, {});'.format(left, expr))
    elif chans[node.left.name] == defs.CONNECT_CLIENT:
      self.out('CLIENT_IN_TAG({}, {});'.format(left, expr))
    else:
      self.out('IN({}, {});'.format(left, expr))
    
  def stmt_alias(self, node, chans):
    """ 
    Generate an alias statement. If the slice target is an array we must use
    some inline assembly to get xcc to load the address for us. Otherwise,
    we can just perform arithmetic on the pointer.
    """
    if node.slice.symbol.type == T_VAR_ARRAY:
      self.asm('add %0, %1, %2', outop=node.left.name, 
          inops=[node.slice.name, '({})*{}'.format(
            self.expr(node.slice.base), defs.BYTES_PER_WORD)])

    elif node.slice.symbol.type == T_REF_ARRAY:
      self.out('{} = {} + ({})*{};'.format(self.elem(node.left), node.slice.name, 
        self.expr(node.slice.base), defs.BYTES_PER_WORD))

  def stmt_connect(self, node, chans):
    
    if node.type == defs.CONNECT_MASTER:
      self.out('{} = {}({}, {});'.format(self.elem(node.left), 
        defs.LABEL_CONNECT_MASTER, self.expr(node.id), self.expr(node.expr)))
    
    elif node.type == defs.CONNECT_SLAVE:
      self.out('{} = {}({}, {});'.format(self.elem(node.left),
        defs.LABEL_CONNECT_SLAVE, self.expr(node.id), self.expr(node.expr)))
    
    elif node.type == defs.CONNECT_SERVER:
      self.out('{} = {}({});'.format(self.elem(node.left),
        defs.LABEL_CONNECT_SERVER, self.expr(node.id)))
    
    elif node.type == defs.CONNECT_CLIENT:
      self.out('{} = {}({}, {});'.format(self.elem(node.left),
        defs.LABEL_CONNECT_CLIENT, self.expr(node.id), self.expr(node.expr)))
    
    else:
      assert 0

  def stmt_if(self, node, chans):
    self.out('if ({})'.format(self.expr(node.cond)))
    self.stmt_block(node.thenstmt, chans)
    if not isinstance(node.elsestmt, ast.StmtSkip):
      self.out('else')
      self.stmt_block(node.elsestmt, chans)

  def stmt_while(self, node, chans):
    self.out('while ({})'.format(self.expr(node.cond)))
    self.stmt_block(node.stmt, chans)
  
  def stmt_for(self, node, chans):
    self.out('for ({0} = {1}; {0} < ({1}+{2}); {0}++)'.format(
      node.index.name, self.expr(node.index.base), 
      self.expr(node.index.count)))
    self.stmt_block(node.stmt, chans)

  def stmt_on(self, node, chans):
    gen_on(self, node, chans)

  def stmt_pcall(self, node, chans):
    self.out('{}({});'.format(
      self.procedure_name(node.name), self.arguments(node.args)))

  def stmt_assert(self, node, chans):
    self.out('ASSERT({});'.format(self.expr(node.expr)))

  def stmt_return(self, node, chans):
    self.out('return {};'.format(self.expr(node.expr)))

  def stmt_skip(self, node, chans):
    pass

  # Statements that have been reduced to a canonical form

  def stmt_server(self, node, chans):
    assert 0

  def stmt_rep(self, node, chans):
    assert 0

  # Expressions =========================================
  # Return their string representation

  def expr_single(self, node):

    # If the elem is an array reference subscript, generate a load
    if isinstance(node.elem, ast.ElemSub):
      if node.elem.symbol.type == T_REF_ARRAY:
        tmp = self.blocker.get_tmp()
        self.asm('ldw %0, %1[%2]', outop=tmp,
            inops=[node.elem.name, self.expr(node.elem.expr)])
        return tmp

    # Otherwise, just return the regular syntax
    return self.elem(node.elem)

  def expr_unary(self, node):
    
    # If the elem is an array reference subscript, generate a load
    if isinstance(node.elem, ast.ElemSub):
      if node.elem.symbol.type == T_REF_ARRAY:
        tmp = self.blocker.get_tmp()
        self.asm('ldw %0, %1[%2]', outop=tmp,
            inops=[node.elem.name, self.expr(node.elem.expr)])
        return '({}{})'.format(op_conversion[node.op], tmp)
    
    # Otherwise, just return the regular syntax
    else:
      return '({}{})'.format(op_conversion[node.op], self.elem(node.elem))

  def expr_binop(self, node):
    
    # If the elem is an array reference subscript, generate a load
    if isinstance(node.elem, ast.ElemSub):
      if node.elem.symbol.type == T_REF_ARRAY:
        tmp = self.blocker.get_tmp()
        self.asm('ldw %0, %1[%2]', outop=tmp,
            inops=[node.elem.name, self.expr(node.elem.expr)])
        return '{} {} {}'.format(tmp,
            op_conversion[node.op], self.expr(node.right))
    
    # Otherwise, just return the regular syntax
    return '{} {} {}'.format(self.elem(node.elem), 
        op_conversion[node.op], self.expr(node.right))
  
  # Elements ============================================
  # Return their string representation

  def elem_group(self, node):
    return '({})'.format(self.expr(node.expr))

  def elem_sub(self, node):
    return '{}[{}]'.format(node.name, self.expr(node.expr))

  def elem_slice(self, node):
    # If source is an array take the address, if reference then just the value
    address = ''+node.name
    if node.symbol.type == T_VAR_ARRAY:
      address = '(unsigned, '+address+')'
    return '({} + ({})*{})'.format(address, self.expr(node.base),
         defs.BYTES_PER_WORD)

  def elem_fcall(self, node):
    return '{}({})'.format(self.procedure_name(node.name), self.arguments(node.args))

  def elem_number(self, node):
    return '{}'.format(node.value)

  def elem_boolean(self, node):
    return '{}'.format(node.value.upper())

  def elem_string(self, node):
    return '{}'.format(node.value)

  def elem_char(self, node):
    return '{}'.format(node.value)

  def elem_id(self, node):
    return node.name

