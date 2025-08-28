# runtime_entities.py

"""
This module defines the core runtime entities used in the CSE (Control Stack Environment) Machine.
These entities represent different types of nodes and closures that are used during
program execution.
"""

class DeltaNode:
    """
    Represents a delta node in the CSE machine, which corresponds to a control structure
    or a function body that needs to be executed.
    
    Attributes:
        index (int): Unique identifier for the delta node, representing the rule number
    """
    def __init__(self, index):
        self.index = index  # Represents the delta rule number

class TupleNode:
    """
    Represents a tuple node in the CSE machine, which holds multiple values.
    
    Attributes:
        index (int): The size of the tuple
    """
    def __init__(self, index):
        self.index = index  # Represents the size of the tuple

class LambdaClosure:
    """
    Represents a lambda closure in the CSE machine, which is a function with its
    environment context.
    
    Attributes:
        index (int): Unique identifier for the lambda closure
        bound_var (str): The variable bound by this lambda
        env_context (int): The environment in which the lambda was defined
    """
    def __init__(self, index):
        self.index = index  # Corresponds to a lambda abstraction
        self.bound_var = None  # The variable bound by this lambda
        self.env_context = None  # The environment in which it was defined

class EtaClosure:
    """
    Represents an eta closure in the CSE machine, which is used for optimization
    and representation of recursive functions.
    
    Attributes:
        index (int): Unique identifier for the eta closure
        bound_var (str): The bound identifier
        env_context (int): The environment associated with this eta closure
    """
    def __init__(self, index):
        self.index = index  # Used for optimization/representation
        self.bound_var = None  # The bound identifier
        self.env_context = None  # The environment associated with this eta
