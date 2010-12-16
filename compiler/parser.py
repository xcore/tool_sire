import ply.yacc as yacc

from lexer import tokens

precedence = (
    ('left', 'LSHIFT', 'RSHIFT', 'AND', 'OR', 'XOR', 'MODULO'),
    ('left', 'PLUS', 'MINUS'),
    ('left', 'MULT', 'DIV'),
    ('right' 'UMINUS')
)

start = 'program'

# Program declaration ====================================================
def p_program(p):
    'program : var_decls proc_decls'
    p[0] = Node("program", None, [p[1], p[2]])

def p_program_error(p):
    'program : error'
    p[0] = None
    p.parser.error = 1

# Variable declarations ==================================================
def p_var_decls(p):
    '''var_decls : empty
                 | var_decl_seq'''
    p[0] = p[1] if len(p)==2 else None
               
def p_var_decl_seq(p):
    '''var_decl_seq : var_decl
                    | var_decl var_decl_seq'''
    p[0] = Node("var_decl_seq", p[1], p[2] if len(p)>2 else None)

def p_var_decl_var(p):
    'var_decl : type name'
    p[0] = Node("var", [p[1], p[2]])

def p_var_decl_var(p):
    '''var_decl : type name LBRACKET RBRACKET
                | type name LBRACKET expr RBRACKET'''
    p[0] = Node("array", [p[1], p[2], p[4] if len(p)==5 else None])

def p_var_decl_val(p):
    'var_decl : VAL name'
    p[0] = Node("val", p[2])

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
    '''proc_decl : PROC name LPAREN formals RPAREN IS var_decls stmt'''
    p[0] = Node("proc", [p[2], p[4], p[7]], p[8]]) 

def p_proc_decl_func(p):
    '''proc_decl : FUNC name LPAREN formals RPAREN IS var_decls stmt'''
    p[0] = Node("func", [p[2], p[4], p[7], p[8]])

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
    'stmt : left INPUT expr'
    p[0] = Node("stmt_in", [p[1], p[3]])

def p_stmt_out(p):
    'stmt : left OUTPUT expr'
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
    'stmt : ON left COLON elem_pcall'
    p[0] = Node("stmt_on", [p[2], p[4]])

def p_stmt_connect(p):
    'stmt : CONNET left TO left COLON left'
    p[0] = Node("stmt_connect", [p[2], p[4], p[6]])

def p_stmt_aliases(p):
    'stmt : elem_name ALIASES elem_name LBRACKET expr DOTS RBRACKET'
    p[0] = Node("stmt_aliases", [p[1], p[3], p[5]])

def p_stmt_return(p):
    'stmt : RETURN expr'
    p[0] = Node("stmt_return", p[2])

def p_stmt_seq_block(p):
    'stmt : START stmt_seq END'
    p[0] = Node("stmt_seq", p[2])
    
def p_stmt_seq(p):
    '''stmt_seq : stmt
                | stmt SEMI stmt_seq'''
    p[0] = Node("stmt_seq", p[1], p[3] if len(p)==4 else None)

def p_stmt_par_block(p):
    '''stmt : START stmt_par END'''
    p[0] = Node("stmt_par", p[2]);

def p_stmt_par(p):
    '''stmt_par : stmt
                | stmt BAR stmt_seq'''
    p[0] = Node("stmt_par", p[1], p[3] if len(p)==4 else None)

# Expressions ============================================================
def p_expr_list(p):
    '''expr_list : expr_seq
                 | empty'''
    p[0] = p[1] if len(p)==2 else None

def p_expr_seq(p):
    '''expr_seq : expr
                | expr COMMA expr_seq'''
    p[0] = Node("expr_seq", p[1], p[3] if len(p)>2 else None)

def p_expr_unary(p):
    '''expr : MINUS expr %prec UMINUS
            | NOT expr %prec UNOT'''
    p[0] = Node("unary", p[1], p[2])

def p_expr_binary_arithmetic(p):
    '''expr : elem PLUS right
            | elem MINUS right
            | elem MULT right
            | elem DIV right
            | elem REM right
            | elem OR right
            | elem AND right
            | elem XOR right
            | elem LSHIFT right
            | elem RSHIFT right'''
    p[0] = Node("binop", p[2], [p[1], p[3]])

def p_expr_binary_relational(p):
    '''expr : elem EQ right
            | elem NE right
            | elem LS right
            | elem LE right
            | elem GR right
            | elem GE right'''
    p[0] = Node("binop", p[2], [p[1], p[3]])

def p_right(p):
    '''right : elem
             | elem AND right
             | elem OR right
             | elem XOR right
             | elem PLUS right
             | elem MULT right'''
    p[0] = Node("binop", p[2], [p[1], p[3]])

# Elements ===============================================================
def p_left_name(p):
    '''left : name'''
    p[0] = Node("name", p[1])
 
def p_left_sub(p):
    '''left: name LBRACKET expr RBRACKET'''
    p[0] = Node("sub", [p[1], p[3]])

def p_elem_fcall(p):
    '''elem : name LPAREN expr_list RPAREN'''
    p[0] = Node("fcall", [p[1],p[3]])

def p_elem_number(p):
    '''elem : NUMBER'''
    p[0] = Node("number", p[1])

def p_elem_boolean_true(p):
    '''elem : TRUE'''
    p[0] = Node("boolean", Node("true"))

def p_elem_boolean_false(p):
    '''elem : FALSE'''
    p[0] = Node("boolean", Node("false"))

def p_elem_string(p):
    '''elem : STRING'''
    p[0] = Node("string", p[1][1:-1])

def p_elem_group(p):
    '''elem : LPAREN expr RPAREN'''
    p[0] = Node("group", p[2])

def p_name(p):
    '''name : ID'''
    p[0] = Node("id", p[1])

# Error rule for syntax errors
def p_error(p):
    print "Syntax error in input!"

# Build the parser
parser = yacc.yacc()

def parse(data, debug=0):
    parser.error = 0
    p = parser.parse(data, debug=debug)
    if parser.error: return None
    return p
