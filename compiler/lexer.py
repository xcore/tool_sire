import ply.lex as lex

# Reserved tokens
reserved = {
    'aliases' : 'ALIASES',
    'chanend' : 'CHANEND',
    'connect' : 'CONNECT',
    'const'   : 'CONST',
    'do'      : 'DO',
    'to'      : 'TO',
    'else'    : 'ELSE',
    'false'   : 'FALSE',
    'for'     : 'FOR',
    'func'    : 'FUNC',
    'if'      : 'IF',
    'int'     : 'INT',
    'is'      : 'IS',
    'on'      : 'ON',
    'proc'    : 'PROC',
    'port'    : 'PORT',
    'return'  : 'RETURN',
    'skip'    : 'SKIP',
    'then'    : 'THEN',
    'true'    : 'TRUE',
    'var'     : 'VAR',
    'while'   : 'WHILE',
}

# All tokens
tokens = [
    # Whitespace
    'IGNORE',
    # Operators
    'PLUS','MINUS','TIMES','DIVIDE','MODULO','OR','AND','NOT','XOR',
    'LSHIFT','RSHIFT','LOR','LAND','LNOT','LT','GT','LE','GE','EQ','NE',
    # Assignment operators
    'ASS','IN','OUT',
    # Delimiters
    'LPAREN','RPAREN','LBRACKET','RBRACKET','LBRACE','RBRACE','COMMA',
    'PERIOD', 'COLON',
    # Separators
    'SEMI','BAR',
    # Literals
    'HEXLITERAL','DECLITERAL','BINLITERAL','CHAR','STRING','COMMENT',
    # Identifiers
    'ID',
] + list(reserved.values())

# Whitespace
t_IGNORE   = r'[ \t]+'

# Operators
t_PLUS     = r'\+'
t_MINUS    = r'-'
t_TIMES    = r'\*'
t_DIVIDE   = r'/'
t_MODULO   = r'%'
t_OR       = r'or'
t_AND      = r'&'
t_NOT      = r'~'
t_XOR      = r'\^'
t_LSHIFT   = r'<<'
t_RSHIFT   = r'>>'
t_LOR      = r'lor'
t_LAND     = r'&&'
t_LNOT     = r'!'
t_LT       = r'<'
t_GT       = r'>'
t_LE       = r'<='
t_GE       = r'>='
t_EQ       = r'='
t_NE       = r'~='

# Assignment operators
t_ASS      = r':='
t_IN       = r'\?'
t_OUT      = r'!'

# Delimeters
t_LPAREN   = r'\('
t_RPAREN   = r'\)'
t_LBRACKET = r'\['
t_RBRACKET = r'\]'
t_LBRACE   = r'\{'
t_RBRACE   = r'\}'
t_COMMA    = r','
t_PERIOD   = r'\.'
t_COLON    = r':'

# Separators
t_SEMI     = r';'
t_BAR      = r'\|'

# Newline
def t_NEWLINE(t):
    r'[\n\r]'
    t.lexer.lineno += len(t.value)

# Comment
def t_COMMENT(t):
    r'%.*'
    pass

# Hexdecimal literal
def t_HEXLITERAL(t):
    r'0[xX][0-9A-Fa-f]+'
    t.value = int(t.value, 16)
    return t

# Decimal literal
def t_DECLITERAL(t):
    r'[0-9]+'
    t.value = int(t.value, 10)
    return t

# Binary literal
def t_BINLITERAL(t):
    r'0[bB][01]+'
    t.value = int(t.value, 2)
    return t

# Character constant
def t_CHAR(t):
    r'\'([^\']|"\\n"|"\\t")\''
    return t

# String literal
def t_STRING(t):
    r'\"[^\"]*\"'
    return t

# Identifiers
def t_ID(t):
    r'[A-Za-z][a-zA-Z0-9_]*'
    t.type = reserved.get(t.value, 'ID')
    return t

# Error handling rule
def t_error(t):
    print "Illegal character '%s'" % t.value[0]
    t.lexer.skip(1)

# Build the lexer
lexer = lex.lex()

# Test it out
data = '''
3 + 4 * 10
  + -20 *2
  '''

# Give the lexer some input
lexer.input(data)

# Tokenize
while True:
    tok = lexer.token()
    if not tok: break
    print tok
