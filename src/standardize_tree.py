# standardize_tree.py

"""
This module implements the standardization process for the RPAL Abstract Syntax Tree (AST).
The standardization process transforms the AST into a form that is easier to execute,
following specific rules for different types of expressions.
"""

from src.rpal_ast_builder import parse_rpal_program
from src.tree_node import TreeNode

def transform_to_standard_form(file_path):
    """
    Main entry point for standardizing an RPAL program.
    
    Args:
        file_path (str): Path to the RPAL source file
        
    Returns:
        TreeNode: The root of the standardized tree
        
    The function:
    1. Parses the input file into an AST
    2. Standardizes the AST according to RPAL rules
    3. Returns the standardized tree
    """
    ast_root = parse_rpal_program(file_path)
    standardized_root = standardize_subtree(ast_root)
    return standardized_root

def standardize_subtree(node):
    """
    Recursively standardizes a subtree according to RPAL rules.
    
    Args:
        node (TreeNode): The root of the subtree to standardize
        
    Returns:
        TreeNode: The standardized subtree
        
    The function handles various RPAL constructs:
    - let expressions
    - where expressions
    - function forms
    - gamma expressions
    - within expressions
    - @ operations
    - and expressions
    - recursive definitions
    """
    # First standardize all children
    for child in node.descendants:
        standardize_subtree(child)

    match node.label:
        # Rule 1: Standardize let expressions
        # let x = E1 in E2 -> gamma(lambda x.E2, E1)
        case "let" if node.descendants[0].label == "=":
            lhs, rhs = node.descendants
            node.descendants[1] = lhs.descendants[1]
            lhs.label = "lambda"
            lhs.descendants[1] = rhs
            node.label = "gamma"

        # Rule 2: Standardize where expressions
        # E1 where x = E2 -> gamma(lambda x.E1, E2)
        case "where" if node.descendants[1].label == "=":
            expr, definition = node.descendants
            node.descendants[0] = definition.descendants[1]
            definition.label = "lambda"
            definition.descendants[1] = expr
            node.descendants[0], node.descendants[1] = definition, node.descendants[0]
            node.label = "gamma"

        # Rule 3: Standardize function forms
        # f x1 x2 ... xn = E -> f = lambda x1.(lambda x2.(...lambda xn.E))
        case "function_form":
            expression = node.descendants.pop()
            current = node
            for _ in range(len(node.descendants) - 1):
                lam = TreeNode("lambda")
                lam.descendants.append(node.descendants.pop(1))
                current.descendants.append(lam)
                current = lam
            current.descendants.append(expression)
            node.label = "="

        # Rule 4: Standardize nested gamma expressions
        # gamma(gamma(E1, E2), E3) -> gamma(E1, gamma(E2, E3))
        case "gamma" if len(node.descendants) > 2:
            expression = node.descendants.pop()
            current = node
            for _ in range(len(node.descendants) - 1):
                lam = TreeNode("lambda")
                lam.descendants.append(node.descendants.pop(1))
                current.descendants.append(lam)
                current = lam
            current.descendants.append(expression)

        # Rule 5: Standardize within expressions
        # within x1 = E1; x2 = E2 -> x2 = gamma(lambda x1.E2, E1)
        case "within" if all(child.label == "=" for child in node.descendants):
            x2 = node.descendants[1].descendants[0]
            gamma_node = TreeNode("gamma")
            lambda_node = TreeNode("lambda")
            lambda_node.descendants.append(node.descendants[0].descendants[0])
            lambda_node.descendants.append(node.descendants[1].descendants[1])
            gamma_node.descendants.extend([lambda_node, node.descendants[0].descendants[1]])
            node.descendants = [x2, gamma_node]
            node.label = "="

        # Rule 6: Standardize @ operations
        # E1 @ E2 -> gamma(E1, E2)
        case "@":
            target = node.descendants.pop(0)
            func = node.descendants[0]
            gamma_inner = TreeNode("gamma")
            gamma_inner.descendants = [func, target]
            node.descendants[0] = gamma_inner
            node.label = "gamma"

        # Rule 7: Standardize and expressions
        # and x1 = E1; x2 = E2 -> (x1, x2) = (E1, E2)
        case "and":
            id_tuple = TreeNode(",")
            expr_tuple = TreeNode("tau")
            for definition in node.descendants:
                id_tuple.descendants.append(definition.descendants[0])
                expr_tuple.descendants.append(definition.descendants[1])
            node.descendants = [id_tuple, expr_tuple]
            node.label = "="

        # Rule 8: Standardize recursive definitions
        # rec x = E -> x = gamma(Y*, lambda x.E)
        case "rec":
            defn = node.descendants.pop()
            defn.label = "lambda"
            gamma_node = TreeNode("gamma")
            gamma_node.descendants.append(TreeNode("<Y*>"))
            gamma_node.descendants.append(defn)
            node.descendants.append(defn.descendants[0])
            node.descendants.append(gamma_node)
            node.label = "="

    return node
