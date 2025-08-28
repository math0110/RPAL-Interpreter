# tree_node.py

"""
This module defines the TreeNode class used for constructing and representing
the Abstract Syntax Tree (AST) and Standard Tree in the RPAL interpreter.
The tree structure is used to represent the hierarchical structure of RPAL programs.
"""

class TreeNode:
    """
    Represents a node in the Abstract Syntax Tree or Standard Tree.
    
    Attributes:
        label (str): The value or operation represented by this node
        descendants (list): List of child nodes
        depth (int): The depth of this node in the tree (used for printing)
    """
    def __init__(self, label):
        """
        Initialize a new tree node.
        
        Args:
            label (str): The value or operation to be stored in this node
        """
        self.label = label
        self.descendants = []
        self.depth = 0

def print_tree_preorder(node):
    """
    Recursively print the tree structure in preorder traversal.
    Each node is indented based on its depth in the tree.
    
    Args:
        node (TreeNode): The root node of the tree to print
        
    The output format is:
    - Each node is printed on a new line
    - Indentation is represented by dots (.)
    - Children are printed after their parent
    """
    if node is None:
        return

    print("." * node.depth + node.label)

    for child in node.descendants:
        child.depth = node.depth + 1
        print_tree_preorder(child)
