# Copyright (c) 2011, James Hanlon, All rights reserved
# This software is freely distributable under a derivative of the
# University of Illinois/NCSA Open Source License posted in
# LICENSE.txt and at <http://github.xcore.com/>

import ply.lex as lex

class Lexer(object):
  """
  A lexer object for the sire langauge.
  """
  def __init__(self, error_func):
    """ 
    Create a new lexer.
    """
    self.error_func = error_func
    self.filename = ''
    self.lineno = 0
    self.lexpos = 0

  def build(self, **kwargs):
    """ 
    Build a lexer from the specification after it has been instantiated
    because PLY warns against calling lex.lex inside __init__.
    """
    self.lexer = lex.lex(object=self, **kwargs)

  def reset(self):
    self.lexer.lineno = 1
  
  def input(self, text):
    self.lexer.input(text)

  def token(self):
    return self.lexer.token()
   
  def data(self):
    return self.lexer.lexdata

  def findcol(self, input, lexpos):
    """ 
    Compute the column given the input and lexpos.
    """
    last_cr = input.rfind('\n', 0, lexpos)
    if last_cr < 0:
      last_cr = 0
    column = (lexpos - last_cr) + 1
    return column

  def _error(self, msg, token):
    """ 
    Generic lexer error.
    """
    self.error_func(msg, token.lineno, 
        self.findcol(self.lexer.lexdata, token.lexpos))
    self.lexer.skip(1)
 
  # Reserved tokens
  reserved = {
    'aliases' : 'ALIASES',
    'assert'  : 'ASSERT',
    'chan'    : 'CHAN',
    'chanend' : 'CHANEND',
    'connect' : 'CONNECT',
    'do'      : 'DO',
    'else'    : 'ELSE',
    'false'   : 'FALSE',
    'for'     : 'FOR',
    'func'    : 'FUNC',
    'from'    : 'FROM',
    'if'      : 'IF',
    'is'      : 'IS',
    'in'      : 'IN',
    'on'      : 'ON',
    'par'     : 'PAR',
    'proc'    : 'PROC',
    'return'  : 'RETURN',
    'skip'    : 'SKIP',
    'then'    : 'THEN',
    'to'      : 'TO',
    'true'    : 'TRUE',
    'val'     : 'VAL',
    'var'     : 'VAR',
    'while'   : 'WHILE',
    'rem'     : 'REM',
    'or'      : 'OR',
    'and'     : 'AND',
    'xor'     : 'XOR',
  }

  # All tokens
  tokens = (
    # Operators
    'PLUS','MINUS','MULT','DIV', #REM
    'NOT', #OR, AND, XOR
    'LSHIFT','RSHIFT','LT','GT','LE','GE','EQ','NE',
    # Assignment operators
    'ASS', 'INP', 'OUT',
    # Delimiters
    'LPAREN','RPAREN','LBRACKET','RBRACKET','START','END','COMMA', 'COLON', 
    # Separators
    'SEQSEP','PARSEP',
    # Literals
    'HEXLITERAL','DECLITERAL','BINLITERAL','CHAR','STRING',
    # Identifiers
    'ID',
  ) + tuple(reserved.values())

  # Operators ================
  
  # Arithmetic
  t_PLUS     = r'\+'
  t_MINUS    = r'-'
  t_MULT     = r'\*'
  t_DIV      = r'/'
  #t_REM 
  
  # Bitwise ops
  #t_OR 
  #t_AND
  #t_XOR
  t_NOT      = r'~'
  t_LSHIFT   = r'<<'
  t_RSHIFT   = r'>>'
  
  # Relational
  t_LT       = r'<'
  t_GT       = r'>'
  t_LE       = r'<='
  t_GE       = r'>='
  t_EQ       = r'='
  t_NE       = r'~='

  # Assignment operators
  t_ASS      = r':='
  t_INP      = r'\?'
  t_OUT      = r'\!'

  # Delimeters
  t_LPAREN   = r'\('
  t_RPAREN   = r'\)'
  t_LBRACKET = r'\['
  t_RBRACKET = r'\]'
  t_START    = r'\{'
  t_END      = r'\}'
  t_COMMA    = r','
  t_COLON    = r':'

  # Separators
  t_SEQSEP   = r';'
  t_PARSEP = r'\|\|'

  # Whitespace
  def t_IGNORE(self, t):
    r'[ \t]+'
    pass

  # Newline
  def t_NEWLINE(self, t):
    r'[\n\r]'
    t.lexer.lineno += 1

  # Comment
  def t_COMMENT(self, t):
    r'%.*'
    pass

  # Hexdecimal literal
  def t_HEXLITERAL(self, t):
    r'0[xX][0-9A-Fa-f]+'
    t.value = int(t.value, 16)
    return t

  # Decimal literal
  def t_DECLITERAL(self, t):
    r'[0-9]+'
    t.value = int(t.value, 10)
    return t

  # Binary literal
  def t_BINLITERAL(self, t):
    r'0[bB][01]+'
    t.value = int(t.value, 2)
    return t

  # Character constant
  def t_CHAR(self, t):
    r'\'([^\']|"\\n"|"\\t")\''
    return t

  # String literal
  def t_STRING(self, t):
    r'\"[^\"]*\"'
    return t

  # Identifiers
  def t_ID(self, t):
    r'[A-Za-z][a-zA-Z0-9_]*'
    t.type = self.reserved.get(t.value, 'ID')
    return t

  # Error handling rule
  def t_error(self, t):
    msg = "Illegal character '%s'" % repr(t.value[0])
    self._error(msg, t)
    t.lexer.skip(1)

