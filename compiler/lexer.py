import ply.lex as lex

# Declare reserved tokens
reserved = {
    'aliases' : 'ALIASES',
    'chanend' : 'CHANEND',
    'connect' : 'CONNECT',
    'do'      : 'DO',
    'to'      : 'TO',
    'else'    : 'ELSE',
    'false'   : 'FALSE',
    'for'     : 'FOR',
    'func'    : 'FUNC',
    'if'      : 'IF',
    'is'      : 'IS',
    'on'      : 'ON',
    'proc'    : 'PROC',
    'port'    : 'PORT',
    'return'  : 'RETURN',
    'skip'    : 'SKIP',
    'then'    : 'THEN',
    'true'    : 'TRUE',
    'val'     : 'VAL',
    'var'     : 'VAR',
    'while'   : 'WHILE'
}   
    
# All tokens
tokens = (
    # Whitespace
    'IGNORE',
    # Operators
    'PLUS','MINUS','MULT','DIV','MOD','OR','AND','NOT','XOR',
    'LSHIFT','RSHIFT','LOR','LAND','LNOT','LT','GT','LE','GE','EQ','NE',
    # Assignment operators
    'EQUALS','INPUT','OUTPUT',
    # Delimiters
    'LPAREN','RPAREN','LBRACKET','RBRACKET','LBRACE','RBRACE','COMMA','PERIOD',
    'COLON',
    # Separators
    'SEMI','BAR',
    # Literals
    'HEXLITERAL','DECLITERAL','BINLITERAL','CHAR','STRING','COMMENT',
    # Identifiers
    'ID',
) + tuple(reserved.values())

# Define regular expressions for simple tokens
t_IGNORE           = r'[ \t]+'

# Operators
t_PLUS             = r'\+'
t_MINUS            = r'-'
t_MULT             = r'\*'
t_DIV              = r'/'
t_MOD              = r'%'
t_OR               = r'or'
t_AND              = r'&'
t_NOT              = r'~'
t_XOR              = r'\^'
t_LSHIFT           = r'<<'
t_RSHIFT           = r'>>'
t_LOR              = r'lor'
t_LAND             = r'land'
t_LNOT             = r'lnot'
t_LT               = r'<'
t_GT               = r'>'
t_LE               = r'<='
t_GE               = r'>='
t_EQ               = r'='
t_NE               = r'~='

# Assignment operators
t_EQUALS           = r'='
t_INPUT            = r'\?'
t_OUTPUT           = r'!'

# Delimeters
t_LPAREN           = r'\('
t_RPAREN           = r'\)'
t_LBRACKET         = r'\['
t_RBRACKET         = r'\]'
t_LBRACE           = r'\{'
t_RBRACE           = r'\}'
t_COMMA            = r','
t_PERIOD           = r'\.'
t_COLON            = r':'

# Separators
t_SEMI             = r';'
t_BAR              = r'\|'

# Define tokens
def t_NEWLINE(t):
    r'[\n\r]'
    t.lexer.lineno += 1

def t_COMMENT(t):
    r'%.*'
    pass

def t_HEXLITERAL(t):
    r'0[xX][0-9A-Fa-f]+'
    t.value = int(t.value[16])
    return t

def t_DECLITERAL(t):
    r'[0-9]+'
    t.value = int(t.value[10])
    return t

def t_BINLITERAL(t):
    r'0[bB][01]+'
    t.value = int(t.value[2])
    return t

def t_CHAR(t):
    r'\'([^\']|"\\n"|"\\t")\''
    return t

def t_STRING(t):
    r'\"[^\"]*\"'
    return t

def t_ID(t):
    r'[A-Za-z][a-zA-Z0-9_]*'
    t.type = reserved.get(t.value, 'ID')
    return t

# Error handling rule
def t_error(t):
    print "Illegal character '%s'" % t.value[0]
    t.lexer.skip(1)

# Build the lexer
#lexer = lex.lex()
lex.lex(debug=0)

