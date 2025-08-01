# screener_module.py

"""
This module implements the screener component of the RPAL interpreter.
The screener processes tokens from the tokenizer, identifies keywords,
and removes unnecessary tokens like whitespace and comments.
"""

from src.tokenizer import scan_input

def run_screener(file_path):
    """
    Processes a source file through the tokenizer and screener.
    
    Args:
        file_path (str): Path to the RPAL source file
        
    Returns:
        tuple: (processed_tokens, has_invalid, first_invalid)
            - processed_tokens: List of valid tokens
            - has_invalid: Boolean indicating if invalid tokens were found
            - first_invalid: The first invalid token found (if any)
    """
    # Define RPAL language keywords
    rpal_keywords = {
        "let", "in", "where", "rec", "fn", "aug", "or", "not", "gr", "ge", "ls",
        "le", "eq", "ne", "true", "false", "nil", "dummy", "within", "and"
    }

    char_buffer = []
    parsed_tokens = []
    has_invalid = False
    first_invalid = None

    # Read and tokenize the source file
    try:
        with open(file_path, 'r') as source:
            for line in source:
                char_buffer.extend(line)
        parsed_tokens = scan_input(char_buffer)

    except FileNotFoundError:
        print("Error: File not found.")
        exit(1)
    except Exception as err:
        print("Unexpected error:", err)
        exit(1)

    # Process the token list backwards to handle deletions and classify keywords
    for idx in range(len(parsed_tokens) - 1, -1, -1):
        token = parsed_tokens[idx]

        # Convert identifiers to keywords if they match RPAL keywords
        if token.category == "<IDENTIFIER>" and token.value in rpal_keywords:
            token.set_as_keyword()

        # Remove whitespace/comments from token stream
        if token.category == "<DELETE>" or token.value == "\n":
            parsed_tokens.pop(idx)

        # Track invalid tokens
        if token.category == "<INVALID>" and not has_invalid:
            has_invalid = True
            first_invalid = token

    # Reassign the "last token" flag if the original last token was deleted
    if parsed_tokens:
        parsed_tokens[-1].last_in_sequence = True

    return parsed_tokens, has_invalid, first_invalid
