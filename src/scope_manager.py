# scope_manager.py

"""
This module implements the scope management system for the RPAL interpreter.
It handles variable scoping, environment creation, and variable bindings
during program execution.
"""

class Scope:
    """
    Represents a scope in the RPAL program, which contains variable bindings
    and maintains relationships with parent and child scopes.
    
    Attributes:
        name (str): Unique identifier for the scope (e.g., "e_0", "e_1")
        label (str): Human-readable label for the scope
        bindings (dict): Maps variable names to their values
        subscopes (list): List of child scopes
        parent (Scope): Reference to the parent scope
    """
    def __init__(self, scope_id, parent_scope):
        """
        Initialize a new scope.
        
        Args:
            scope_id (int): Unique identifier for this scope
            parent_scope (Scope): The parent scope, or None for global scope
        """
        self.name = "e_" + str(scope_id)
        self.label = f"env_{scope_id}"
        self.bindings = {}
        self.subscopes = []
        self.parent = parent_scope

    def attach_child_scope(self, child_scope):
        """
        Link a child scope to this scope and inherit variable bindings.
        
        Args:
            child_scope (Scope): The child scope to attach
        """
        self.subscopes.append(child_scope)
        child_scope.bindings.update(self.bindings)

    def bind_variable(self, identifier, value):
        """
        Assign a value to a variable in this scope.
        
        Args:
            identifier (str): The name of the variable
            value: The value to bind to the variable
        """
        self.bindings[identifier] = value
