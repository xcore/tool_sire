import ply.yacc as yacc

from lexer import tokens

start = 'program'

# Program declaration
def p_program(p):
    'const_decls port_decls var_decls proc_decls'
    p[0] = Node("program", [p[1], p[2], p[3], p[4]])

# Constant declarations
def p_const_decls(p):
    '''const_decls : empty
                | CONST const_decls_seq'''
    p[0] = Node("const_decls", None if len(p)==1 else p[3])

def p_const_decl_seq(p):
    '''const_decl_seq : const_decl
                      | const_decl COMMA const_decl_seq'''
    p[0] = Node("const_decl_seq", p[1], None if len(p)==2 else p[4])

def p_const_decl(p):
    '''const_decl : name ASS expr'''
    p[0] = Node("const_decl", p[1], p[3])

# Port declarations
def p_port_decls(p):
    '''port_decls : empty
                  | PORT port_decls_seq'''
    p[0] = Node("port_decls", None if len(p)==1 else p[3])

def p_port_decl_seq(p):
    '''port_decl_seq : port_decl
                     | port_decl COMMA port_decl_seq'''
    p[0] = Node("port_decl_seq", p[1], None if len(p)==2 else p[4])

def p_port_decl(p):
    '''port_decl : name COLON expr'''
    p[0] = Node("port_decl", p[1], p[3])

# Variable declarations
def p_var_decls(p):
    '''var_decls : empty
                 | VAR var_decls_seq'''
    p[0] = Node("var_decls", None if len(p)==1 else p[3])

def p_var_decl_seq(p):
    '''var_decl_seq : var_decl
                    | var_decl COMMA var_decl_seq'''
    p[0] = Node("var_decl_seq", p[1], None if len(p)==2 else p[4])

def p_var_decl(p):
    '''var_decl : id_list COLON type_decl'''
    p[0] = Node("var_decl", p[1], p[3])

def p_var_id_list(p):
    '''var_id_list : var_id
                   | var_id COMMA id_list'''
    p[0] = Node("var_id_list", p[1], None if len(p)==2 else p[4])

def p_var_id(p):
    '''var_id : name'''
    p[0] = Node("var_id", p[1])

# Type declarations
def p_type_decl_single(p):
    '''type_decl : type'''
    p[0] = Node("type_decl_single", p[1])

def p_type_decl_alias(p):
    '''type_decl : type LBRACKET RBRCKET'''
    p[0] = Node("type_decl_alias", p[1])

def p_type_decl_array(p):
    '''type_decl : type LBRACKET expr RBRACKET'''
    p[0] = Node("type_decl_array", p[1], p[3])

def p_type_id(p):
    '''type_id : INT 
               | CHAN'''
    p[0] = Node("type_id", p[1])

# Procedure declarations
def p_proc_decls(p):
    '''proc_decls : proc_decl_seq
                  | empty'''
    p[0] = Node("proc_decls", p[1] if len(p)==2 else None)

def p_proc_decl_seq(p):
    '''proc_decl_seq : proc_decl
                     | proc_decl proc_decl_seq'''
    p[0] = Node("proc_decl_seq", p[1], p[2] if len(p)==3 else None)

def p_proc_decl_proc(p):
    '''proc_decl : PROC name LPAREN formals RPAREN IS var_decls stmt'''
    p[0] = Node("proc_decl_proc", [p[2], p[4], p[7]], p[8]) 

def p_proc_decl_func(p):
    '''proc_decl : FUNC name LPAREN formals RPAREN IS var_decls stmt'''
    p[0] = Node("proc_decl_func", [p[2], p[4], p[7]], p[8])

# Formal declarations
def p_formals(p):
    '''formals : formals_seq
               | empty'''
    p[0] = Node("formals", p[1] if len(p)==2 else None)

def p_formals_seq(p):
    '''formals_seq : param_decl_seq COLON param_type_decl
                   | param_decl_seq COLON param_type_decl SEMI formals_seq'''
    p[0] = Node("formals_seq", [p[1], p[3]], p[5] if len(p)==6 else None)

def p_param_decl_seq(p):
    '''param_decl_seq : var_id
                      | var_id COMMA param_decl_seq'''
    p[0] = Node("param_decl_seq", p[1], p[3] if len(p)==4 else None)

def p_param_type_decl_single(p):
    '''param_type_decl : type'''
    p[0] = Node("param_type_decl_single", p[1])

def p_param_type_decl_alias(p):
    '''param_type_decl : type LBRACKET RBRACKET'''
    p[0] = Node("param_type_decl_alias", p[1])

# Statements
def p_stmt_skip(p):
    '''stmt : SKIP'''
    p[0] = Node("stmt_skip")

def p_stmt_proc_call(p):
    '''stmt : name LPAREN expr_list RPAREN'''
    p[0] = Node("stmt_proc_call", [p[1], p[3]])

def p_stmt_ass(p):
    '''stmt : left ASS expr'''
    p[0] = Node("stmt_ass", [p[1], p[3]])

def p_stmt_input(p):
    '''stmt : left INPUT expr'''
    p[0] = Node("stmt_input", [p[1], p[3]])

def p_stmt_output(p):
    '''stmt : left OUTPUT expr'''
    p[0] = Node("stmt_output", [p[1], p[3]])

def p_stmt_if(p):
    '''stmt : IF expr THEN stmt ELSE stmt'''
    p[0] = Node("stmt_if", [p[2], p[4], p[6]])

def p_stmt_while(p):
    '''stmt : WHILE expr DO stmt'''
    p[0] = Node("stmt_while", [p[2], p[4]])

def p_stmt_for(p):
    '''stmt : FOR left ASS expr TO expr DO stmt'''
    p[0] = Node("stmt_for", [p[2], p[4], p[6], p[8]])

def p_stmt_on(p):
    '''stmt : ON left COLON elem_pcall'''
    p[0] = Node("stmt_on", [p[2], p[4]])

def p_stmt_connect(p):
    '''stmt : CONNET left TO left COLON left'''
    p[0] = Node("stmt_connect", [p[2], p[4], p[6]])

def p_stmt_aliases(p):
    '''stmt : elem_name ALIASES elem_name LBRACKET expr DOTS RBRACKET'''
    p[0] = Node("stmt_aliases", [p[1], p[3], p[5])

def p_stmt_return(p):
    '''stmt : RETURN expr'''
    p[0] = Node("stmt_return", p[2])

def p_stmt_seq_block(p):
    '''stmt : START stmt_seq END'''
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

# Expressions
def p_expr_list(p):
    '''expr_list : expr_list_
                 | empty'''
    p[0] = p[1] if len(p)==2 else None

def p_expr_list_(p):
    '''expr_list_ : expr
                  | expr COMMA expr_list_'''
    p[0] = Node("expr_list", p[1], p[3] if len(p)==4 else None)

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
    p[0] = Node("binop", [p[1], p[3]], p[2])

def p_expr_binary_relational(p):
    '''expr : elem EQ right
            | elem NE right
            | elem LS right
            | elem LE right
            | elem GR right
            | elem GE right'''
    p[0] = Node("binop", [p[1], p[3]], p[2])

def p_right(p):
    '''right : elem
             | elem AND right
             | elem OR right
             | elem XOR right
             | elem PLUS right
             | elem MULT right'''
    p[0] = Node("binop", [p[1], p[3]], p[2])

# Elements
def p_left_name(p):
    '''left : name'''
    p[0] = Node("elem_name", p[1])
 
def p_left_sub(p):
    '''left: name LBRACKET expr RBRACKET'''
    p[0] = Node("elem_sub", [p[1],p[3]])

def p_elem_name(p):
    '''elem : name'''
    p[0] = Node("elem_name", p[1]);

def p_elem_sub(p):
    '''elem : name LBRACKET expr RBRACKET'''
    p[0] = Node("elem_sub", [p[1],p[3]])

def p_elem_fncall(p):
    '''elem : name LPAREN expr_list RPAREN'''
    p[0] = Node("elem_fncall", [p[1],p[3]])

def p_elem_number(p):
    '''elem : NUMBER'''
    p[0] = Node("elem_number", p[1])

def p_elem_boolean_true(p):
    '''elem : TRUE'''
    p[0] = Node("elem_boolean", Node("true"))

def p_elem_boolean_false(p):
    '''elem : FALSE'''
    p[0] = Node("elem_boolean", Node("false"))

def p_elem_string(p):
    '''elem : STRING'''
    p[0] = Node("elem_string", p[1])

def p_elem_group(p):
    '''elem : LPAREN expr RPAREN'''
    p[0] = Node("elem_group", p[2])

def p_name(p):
    '''name : ID'''
    p[0] = Node("name", p[1])
