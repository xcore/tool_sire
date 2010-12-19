import ply.yacc as yacc
from ast import Node

from lexer import tokens, lexer

precedence = (
    ('nonassoc', 'LT', 'GT', 'LE', 'GE', 'EQ', 'NE'), 
    ('left', 'LSHIFT', 'RSHIFT'),
    ('left', 'AND', 'OR', 'XOR', 'MOD'),
    ('left', 'PLUS', 'MINUS'),
    ('left', 'MULT', 'DIV'),
    ('right', 'UMINUS', 'UNOT')
)

start = 'program'

# Program declaration ====================================================
def p_program(p):
    'program : var_decls proc_decls'
    p[0] = Node("program", p.lineno(1), find_col(lexer.lexdata, p), 
            None, [p[1], p[2]])

def p_program_error(p):
    'program : error'
    print "Syntax error"
    p[0] = None
    p.parser.error = 1

# Variable declarations ==================================================
def p_var_decls(p):
    '''var_decls : empty
                 | var_decl_seq'''
    p[0] = p[1] if len(p)==2 else None
               
def p_var_decl_seq(p):
    '''var_decl_seq : var_decl SEMI
                    | var_decl SEMI var_decl_seq'''
    p[0] = Node("var_decl_seq", p[1], p[2] if len(p)>2 else None)

def p_var_decl_seq_err(p):
    'var_decl_seq : error SEMI'
    print "Syntax error at line {0}:{1}".format(p.lineno(1), p.lexpos(1))
    parser.errok()

def p_var_decl_var(p):
    'var_decl : type name'
    p[0] = Node("var", [p[1], p[2]])

def p_var_decl_array(p):
    '''var_decl : type name LBRACKET RBRACKET
                | type name LBRACKET expr RBRACKET'''
    p[0] = Node("array", [p[1], p[2], p[4] if len(p)==5 else None])

def p_var_decl_val(p):
    'var_decl : VAL name ASS expr'
    p[0] = Node("val", p[2], p[4])

def p_var_decl_port(p):
    'var_decl : PORT name COLON expr'
    p[0] = Node("port", [p[2], p[4]])

# Types ==================================================================
def p_type_id(p):
    '''type : VAR
            | CHAN'''
    p[0] = p[1]

# Procedure declarations =================================================
def p_proc_decls(p):
    '''proc_decls : proc_decl_seq
                  | empty'''
    p[0] = p[1] if len(p)==2 else None

def p_proc_decl_seq(p):
    '''proc_decl_seq : proc_decl
                     | proc_decl proc_decl_seq'''
    p[0] = Node("proc_decl_seq", p[1], p[2] if len(p)>2 else None)

def p_proc_decl_proc(p):
    'proc_decl : PROC name LPAREN formals RPAREN IS var_decls stmt'
    p[0] = Node("proc", [p[2], p[4], p[7], p[8]]) 

# Proc error
def p_proc_decl_proc_err(p):
    '''proc_decl : PROC error IS var_decls stmt'''
    print "Syntax error at line {0}:{1}".format(p.lineno(1), p.lexpos(1))
    parser.errok()

def p_proc_decl_func(p):
    'proc_decl : FUNC name LPAREN formals RPAREN IS var_decls stmt'
    p[0] = Node("func", [p[2], p[4], p[7], p[8]])

# Func error
def p_proc_decl_func_err(p):
    '''proc_decl : FUNC error IS var_decls stmt'''
    print "Syntax error at line {0}:{1}".format(p.lineno(1), p.lexpos(1))
    parser.errok()

# Formal declarations ====================================================
def p_formals(p):
    '''formals : empty
               | formals_seq'''
    p[0] = p[1] if len(p)==2 else None

def p_formals_seq(p):
    '''formals_seq : param_decl
                   | param_decl COMMA formals_seq'''
    p[0] = Node("formals_seq", p[1], p[3] if len(p)>2 else None)

def p_param_decl_var(p):
    'param_decl : name'
    p[0] = Node("var", p[1])

def p_param_decl_val(p):
    'param_decl : VAL name'
    p[0] = Node("val", p[1])

def p_param_decl_chanend(p):
    'param_decl : CHANEND name'
    p[0] = Node("chanend", p[1])

def p_param_decl_alias(p):
    'param_decl : name LBRACKET RBRACKET'
    p[0] = Node("alias", p[1])

# Statements =============================================================
def p_stmt_skip(p):
    'stmt : SKIP'
    p[0] = Node("stmt_skip")

def p_stmt_pcall(p):
    'stmt : name LPAREN expr_list RPAREN'
    p[0] = Node("stmt_pcall", [p[1], p[3]])

def p_stmt_ass(p):
    'stmt : left ASS expr'
    p[0] = Node("stmt_ass", [p[1], p[3]])

def p_stmt_in(p):
    'stmt : left IN expr'
    p[0] = Node("stmt_in", [p[1], p[3]])

def p_stmt_out(p):
    'stmt : left OUT expr'
    p[0] = Node("stmt_out", [p[1], p[3]])

def p_stmt_if(p):
    'stmt : IF expr THEN stmt ELSE stmt'
    p[0] = Node("stmt_if", [p[2], p[4], p[6]])

def p_stmt_while(p):
    'stmt : WHILE expr DO stmt'
    p[0] = Node("stmt_while", [p[2], p[4]])

def p_stmt_for(p):
    'stmt : FOR left ASS expr TO expr DO stmt'
    p[0] = Node("stmt_for", [p[2], p[4], p[6], p[8]])

def p_stmt_on(p):
    'stmt : ON left COLON name LPAREN expr_list RPAREN'
    p[0] = Node("stmt_on", p[2], Node("pcall", [p[4], p[6]]))

def p_stmt_connect(p):
    'stmt : CONNECT left TO left COLON left'
    p[0] = Node("stmt_connect", [p[2], p[4], p[6]])

def p_stmt_aliases(p):
    'stmt : name ALIASES name LBRACKET expr DOTS RBRACKET'
    p[0] = Node("stmt_aliases", [p[1], p[3], p[5]])

def p_stmt_return(p):
    'stmt : RETURN expr'
    p[0] = Node("stmt_return", p[2])

# Seq block
def p_stmt_seq_block(p):
    'stmt : START stmt_seq END'
    p[0] = p[2]

# Seq
def p_stmt_seq(p):
    '''stmt_seq : stmt
                | stmt SEMI stmt_seq'''
    p[0] = Node("stmt_seq", p[1], p[3] if len(p)==4 else None)

# Seq error
def p_stmt_seq_err(p):
    'stmt_seq : error SEMI'
    print "Syntax error at {0} {1}".format(p.lineno(1), p.lexpos(1))
    parser.errok()

# Par block
def p_stmt_par_block(p):
    'stmt : START stmt_par END'
    p[0] = p[2]

# Par
def p_stmt_par(p):
    '''stmt_par : stmt BAR stmt
                | stmt BAR stmt_par'''
    p[0] = Node("stmt_par", p[1], p[3] if len(p)==4 else None)

# Par error
def p_stmt_par_err(p):
    'stmt_par : error BAR'
    print "Syntax error at {0} {1}".format(p.lineno(1), p.lexpos(1))
    parser.errok()

# Expressions ============================================================
def p_expr_list(p):
    '''expr_list : expr_seq
                 | empty'''
    p[0] = p[1] if len(p)==2 else None

def p_expr_seq(p):
    '''expr_seq : expr
                | expr COMMA expr_seq'''
    p[0] = Node("expr_seq", p[1], p[3] if len(p)>2 else None)

def p_expr_sinle(p):
    'expr : elem' 
    p[0] = p[1]

def p_expr_unary(p):
    '''expr : MINUS elem %prec UMINUS
            | NOT elem %prec UNOT'''
    p[0] = Node("unary", p[1], p[2] if len(p)>2 else None)

def p_expr_binary_arithmetic(p):
    '''expr : elem PLUS right
            | elem MINUS right
            | elem MULT right
            | elem DIV right
            | elem MOD right
            | elem OR right
            | elem AND right
            | elem XOR right
            | elem LSHIFT right
            | elem RSHIFT right'''
    p[0] = Node("binop", p[2], [p[1], p[3]])

def p_expr_binary_relational(p):
    '''expr : elem LT right
            | elem GT right
            | elem LE right
            | elem GE right
            | elem EQ right
            | elem NE right'''
    p[0] = Node("binop", p[2], [p[1], p[3]])

def p_right_sinle(p):
    'right : elem'
    p[0] = p[1]

def p_right(p):
    '''right : elem AND right
             | elem OR right
             | elem XOR right
             | elem PLUS right
             | elem MULT right'''
    p[0] = Node("binop", p[2], [p[1], p[3]])

# Elements ===============================================================
def p_left_name(p):
    'left : name'
    p[0] = p[1]
 
def p_left_sub(p):
    'left : name LBRACKET expr RBRACKET'
    p[0] = Node("sub", [p[1], p[3]])

def p_elem_name(p):
    'elem : name'
    p[0] = p[1]

def p_elem_sub(p):
    'elem : name LBRACKET expr RBRACKET'
    p[0] = Node("sub", [p[1], p[3]])

def p_elem_fcall(p):
    'elem : name LPAREN expr_list RPAREN'
    p[0] = Node("fcall", [p[1], p[3]])

def p_elem_number(p):
    '''elem : HEXLITERAL
            | DECLITERAL
            | BINLITERAL'''
    p[0] = Node("number", p[1])

def p_elem_boolean_true(p):
    'elem : TRUE'
    p[0] = Node("boolean", "true")

def p_elem_boolean_false(p):
    'elem : FALSE'
    p[0] = Node("boolean", "false")

def p_elem_string(p):
    'elem : STRING'
    p[0] = Node("string", p[1][1:-1])

def p_elem_char(p):
    'elem : CHAR'
    p[0] = Node("char", p[1])

def p_elem_group(p):
    'elem : LPAREN expr RPAREN'
    p[0] = Node("group", p[2])

# Identifier
def p_name(p):
    'name : ID'
    p[0] = Node("id", p[1])

# Empty rule
def p_empty(p):
    'empty :'
    pass

# Compute column. 
#     input is the input text string
#     token is a token instance
def find_col(input,token):
    last_cr = input.rfind('\n',0,token.lexpos)
    if last_cr < 0:
        last_cr = 0
    column = (token.lexpos - last_cr) + 1
    return column

# Error rule for syntax errors
def p_error(p):
    print "Syntax error: token {0} '{1}' at {2}:{3}".format(
        p.type, p.value, p.lineno, find_col(lexer.lexdata, p))
    pass

# Build the parser
parser = yacc.yacc(debug=False)

def parse(data, debug=0):
    parser.error = 0
    p = parser.parse(data, debug=debug)
    if parser.error: return None
    return p
