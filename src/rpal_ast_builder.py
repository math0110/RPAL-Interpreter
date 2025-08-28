# rpal_ast_builder.py

"""
This module implements the Abstract Syntax Tree (AST) builder for the RPAL interpreter.
It uses recursive descent parsing to construct the AST from the token stream.
The parser follows the RPAL grammar rules to build a tree representation of the program.
"""

from src.screener_module import run_screener
from src.custom_stack import CustomStack
from src.tree_node import TreeNode, print_tree_preorder

# Global stack used for building the abstract syntax tree
tree_stack = CustomStack("AST")

def create_node(label, num_descendants):
    """
    Creates a new tree node and populates it with its descendants from the stack.
    
    Args:
        label (str): The label for the new node
        num_descendants (int): Number of child nodes to attach
        
    The function:
    1. Creates a new TreeNode
    2. Pops the required number of descendants from the stack
    3. Attaches them to the new node
    4. Pushes the new node onto the stack
    """
    node = TreeNode(label)
    node.descendants = [None] * num_descendants

    for i in range(num_descendants):
        if tree_stack.is_empty():
            print("Error: AST stack unexpectedly empty.")
            exit(1)
        node.descendants[num_descendants - i - 1] = tree_stack.pop()

    tree_stack.push(node)

def display_tree(root):
    """Prints the tree structure in preorder traversal."""
    print_tree_preorder(root)

def consume(expected_value):
    """
    Consumes a token from the input stream if it matches the expected value.
    
    Args:
        expected_value (str): The expected token value
        
    Raises:
        SystemExit: If the token doesn't match the expected value
    """
    if token_stream[0].value != expected_value:
        print(f"Syntax error on line {token_stream[0].line_number}: expected '{expected_value}', got '{token_stream[0].value}'")
        exit(1)

    if not token_stream[0].last_in_sequence:
        del token_stream[0]
    else:
        if token_stream[0].category != ")":
            token_stream[0].category = ")"

def parse_rpal_program(input_file):
    """
    Main entry point for parsing an RPAL program.
    
    Args:
        input_file (str): Path to the RPAL source file
        
    Returns:
        TreeNode: The root of the constructed AST
        
    The function:
    1. Reads and screens the input file
    2. Validates the tokens
    3. Constructs the AST using recursive descent parsing
    4. Returns the root node of the AST
    """
    global token_stream
    token_stream, has_invalid_token, bad_token = run_screener(input_file)

    if has_invalid_token:
        print(f"Invalid token found on line {bad_token.line_number}: {bad_token.value}")
        exit(1)

    parse_E()

    if not tree_stack.is_empty():
        return tree_stack.pop()
    else:
        print("Error: AST stack unexpectedly empty.")
        exit(1)

# --- Start of Recursive Descent Parsing Procedures ---

def parse_E():
    """
    Parses an expression (E) in the RPAL grammar.
    Handles let expressions and function definitions.
    """
    if token_stream[0].value == "let":
        consume("let")
        parse_D()
        if token_stream[0].value == "in":
            consume("in")
            parse_E()
            create_node("let", 2)
        else:
            report_expected("'in'")
    elif token_stream[0].value == "fn":
        consume("fn")
        count = 0
        while token_stream[0].category == "<IDENTIFIER>" or token_stream[0].value == "(":
            parse_Vb()
            count += 1
        if count == 0:
            report_expected("identifier or '('")
        consume(".")
        parse_E()
        create_node("lambda", count + 1)
    else:
        parse_Ew()

def parse_Ew():
    """
    Parses an expression with where clause (Ew).
    Handles where expressions and tuple expressions.
    """
    parse_T()
    if token_stream[0].value == "where":
        consume("where")
        parse_Dr()
        create_node("where", 2)

def parse_T():
    """
    Parses a tuple expression (T).
    Handles comma-separated expressions and tau nodes.
    """
    parse_Ta()
    count = 0
    while token_stream[0].value == ",":
        consume(",")
        parse_Ta()
        count += 1
    if count > 0:
        create_node("tau", count + 1)

def parse_Ta():
    """
    Parses a tuple with augment operations (Ta).
    Handles the aug operator for tuple concatenation.
    """
    parse_Tc()
    while token_stream[0].value == "aug":
        consume("aug")
        parse_Tc()
        create_node("aug", 2)

def parse_Tc():
    """
    Parses a conditional expression (Tc).
    Handles if-then-else expressions.
    """
    parse_B()
    if token_stream[0].value == "->":
        consume("->")
        parse_Tc()
        consume("|")
        parse_Tc()
        create_node("->", 3)

def parse_B():
    """
    Parses a boolean expression (B).
    Handles logical OR operations.
    """
    parse_Bt()
    while token_stream[0].value == "or":
        consume("or")
        parse_Bt()
        create_node("or", 2)

def parse_Bt():
    """
    Parses a boolean term (Bt).
    Handles logical AND operations.
    """
    parse_Bs()
    while token_stream[0].value == "&":
        consume("&")
        parse_Bs()
        create_node("&", 2)

def parse_Bs():
    """
    Parses a boolean secondary (Bs).
    Handles NOT operations.
    """
    if token_stream[0].value == "not":
        consume("not")
        parse_Bp()
        create_node("not", 1)
    else:
        parse_Bp()

def parse_Bp():
    """
    Parses a boolean primary (Bp).
    Handles comparison operations.
    """
    parse_A()
    ops = ["gr", ">", "ge", ">=", "ls", "<", "le", "<=", "eq", "ne"]
    if token_stream[0].value in ops:
        op = token_stream[0].value
        consume(op)
        parse_A()
        canonical = {
            ">": "gr", ">=": "ge",
            "<": "ls", "<=": "le"
        }.get(op, op)
        create_node(canonical, 2)

def parse_A():
    """
    Parses an arithmetic expression (A).
    Handles addition and subtraction.
    """
    if token_stream[0].value == "+":
        consume("+")
        parse_At()
    elif token_stream[0].value == "-":
        consume("-")
        parse_At()
        create_node("neg", 1)
    else:
        parse_At()

    while token_stream[0].value in ["+", "-"]:
        op = token_stream[0].value
        consume(op)
        parse_At()
        create_node(op, 2)

def parse_At():
    """
    Parses an arithmetic term (At).
    Handles multiplication and division.
    """
    parse_Af()
    while token_stream[0].value in ["*", "/"]:
        op = token_stream[0].value
        consume(op)
        parse_Af()
        create_node(op, 2)

def parse_Af():
    """
    Parses an arithmetic factor (Af).
    Handles exponentiation.
    """
    parse_Ap()
    if token_stream[0].value == "**":
        consume("**")
        parse_Af()
        create_node("**", 2)

def parse_Ap():
    """
    Parses an arithmetic primary (Ap).
    Handles function application and @ operations.
    """
    parse_R()
    while token_stream[0].value == "@":
        consume("@")
        if token_stream[0].category == "<IDENTIFIER>":
            create_node("<ID:" + token_stream[0].value + ">", 0)
            consume(token_stream[0].value)
            parse_R()
            create_node("@", 3)
        else:
            report_expected("identifier")

def parse_R():
    """
    Parses an R-expression.
    Handles function application and gamma nodes.
    """
    parse_Rn()
    while token_stream[0].category in ["<IDENTIFIER>", "<INTEGER>", "<STRING>"] or token_stream[0].value in ["true", "false", "nil", "dummy", "("]:
        parse_Rn()
        create_node("gamma", 2)

def parse_Rn():
    """
    Parses an Rn-expression.
    Handles identifiers, literals, and parenthesized expressions.
    """
    val = token_stream[0].value
    typ = token_stream[0].category
    if typ == "<IDENTIFIER>":
        consume(val)
        create_node("<ID:" + val + ">", 0)
    elif typ == "<INTEGER>":
        consume(val)
        create_node("<INT:" + val + ">", 0)
    elif typ == "<STRING>":
        consume(val)
        create_node("<STR:" + val + ">", 0)
    elif val in ["true", "false", "nil", "dummy"]:
        consume(val)
        create_node("<" + val + ">", 0)
    elif val == "(":
        consume("(")
        parse_E()
        consume(")")
    else:
        report_expected("literal, identifier or '('")

def parse_D():
    """
    Parses a definition (D).
    Handles within expressions and multiple definitions.
    """
    parse_Da()
    if token_stream[0].value == "within":
        consume("within")
        parse_D()
        create_node("within", 2)

def parse_Da():
    """
    Parses a Da-expression.
    Handles and expressions for multiple definitions.
    """
    parse_Dr()
    count = 0
    while token_stream[0].value == "and":
        consume("and")
        parse_Dr()
        count += 1
    if count > 0:
        create_node("and", count + 1)

def parse_Dr():
    """
    Parses a Dr-expression.
    Handles recursive definitions.
    """
    if token_stream[0].value == "rec":
        consume("rec")
        parse_Db()
        create_node("rec", 1)
    else:
        parse_Db()

def parse_Db():
    """
    Parses a Db-expression.
    Handles function definitions and variable bindings.
    """
    val = token_stream[0].value
    if val == "(":
        consume("(")
        parse_D()
        consume(")")
    elif token_stream[0].category == "<IDENTIFIER>":
        consume(val)
        create_node("<ID:" + val + ">", 0)
        if token_stream[0].value in [",", "="]:
            parse_Vl()
            consume("=")
            parse_E()
            create_node("=", 2)
        else:
            count = 0
            while token_stream[0].category in ["<IDENTIFIER>"] or token_stream[0].value == "(":
                parse_Vb()
                count += 1
            if count == 0:
                report_expected("identifier or '('")
            consume("=")
            parse_E()
            create_node("function_form", count + 2)

def parse_Vb():
    """
    Parses a Vb-expression.
    Handles variable bindings in function definitions.
    """
    val = token_stream[0].value
    if token_stream[0].category == "<IDENTIFIER>":
        consume(val)
        create_node("<ID:" + val + ">", 0)
    elif val == "(":
        consume("(")
        inner_val = token_stream[0].value
        if inner_val == ")":
            consume(")")
            create_node("()", 0)
        elif token_stream[0].category == "<IDENTIFIER>":
            consume(inner_val)
            create_node("<ID:" + inner_val + ">", 0)
            parse_Vl()
            consume(")")
        else:
            report_expected("identifier or ')'")
    else:
        report_expected("identifier or '('")

def parse_Vl():
    """
    Parses a Vl-expression.
    Handles comma-separated variable lists.
    """
    count = 0
    while token_stream[0].value == ",":
        consume(",")
        if token_stream[0].category == "<IDENTIFIER>":
            val = token_stream[0].value
            consume(val)
            create_node("<ID:" + val + ">", 0)
            count += 1
        else:
            report_expected("identifier")
    if count > 0:
        create_node(",", count + 1)

def report_expected(expected):
    """
    Reports a syntax error when an expected token is not found.
    
    Args:
        expected (str): Description of the expected token
    """
    print(f"Syntax error on line {token_stream[0].line_number}: '{expected}' expected")
    exit(1)
