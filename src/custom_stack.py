# custom_stack.py

"""
This module implements a custom stack data structure used in both the parser
and the CSE (Control Stack Environment) machine. It provides specialized
functionality for handling RPAL program elements.
"""

class CustomStack:
    """
    A custom stack implementation with additional functionality for RPAL processing.
    
    Attributes:
        _elements (list): The underlying list storing stack elements
        label (str): Identifier for the stack's context (e.g., "AST" or "CSE")
    """
    def __init__(self, context_label):
        """
        Initialize a new custom stack.
        
        Args:
            context_label (str): The context in which this stack is used
        """
        self._elements = []
        self.label = context_label

    def __repr__(self):
        """String representation of the stack for debugging."""
        return str(self._elements)

    def __getitem__(self, idx):
        """Allow indexing into the stack using square bracket notation."""
        return self._elements[idx]

    def __setitem__(self, idx, val):
        """Allow setting a value at a specific index."""
        self._elements[idx] = val

    def __reversed__(self):
        """Support iteration over the stack in reverse order."""
        return reversed(self._elements)

    def push(self, value):
        """
        Add a new item to the top of the stack.
        
        Args:
            value: The item to add to the stack
        """
        self._elements.append(value)

    def pop(self):
        """
        Remove and return the item on top of the stack.
        
        Returns:
            The top item from the stack
            
        Raises:
            SystemExit: If the stack is empty
        """
        if not self.is_empty():
            return self._elements.pop()
        else:
            if self.label == "CSE":
                print("Error: CSE execution stack unexpectedly empty.")
            else:
                print("Error: AST construction stack unexpectedly empty.")
            exit(1)

    def is_empty(self):
        """
        Check if the stack is currently empty.
        
        Returns:
            bool: True if the stack is empty, False otherwise
        """
        return len(self._elements) == 0
