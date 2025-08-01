# token_model.py

"""
This module defines the LexicalToken class which represents tokens in the RPAL language.
Each token contains information about its value, category, and position in the source code.
"""

class LexicalToken:
    """
    Represents a lexical token in the RPAL language.
    
    Attributes:
        value (str): The actual text value of the token
        category (str): The type/category of the token (e.g., <IDENTIFIER>, <INTEGER>)
        line_number (int): The line number where this token appears in the source
        first_in_sequence (bool): Flag indicating if this is the first token in a sequence
        last_in_sequence (bool): Flag indicating if this is the last token in a sequence
    """
    def __init__(self, value, category, line_number):
        self.value = value
        self.category = category
        self.line_number = line_number
        self.first_in_sequence = False
        self.last_in_sequence = False

    def __str__(self):
        """String representation of the token for debugging purposes."""
        return f"{self.value} : {self.category}"

    def mark_as_first(self):
        """Marks this token as the first one in a sequence."""
        self.first_in_sequence = True

    def mark_as_last(self):
        """Marks this token as the last one in a sequence (important for parsing)."""
        self.last_in_sequence = True

    def set_as_keyword(self):
        """Designates this token as a keyword in the RPAL language."""
        self.category = "<KEYWORD>"
