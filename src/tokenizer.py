# tokenizer.py

"""
This module implements the lexical analyzer (tokenizer) for the RPAL language.
It converts source code into a sequence of tokens that can be processed by the parser.
"""

from src.token_model import LexicalToken

def scan_input(input_chars): 
    """
    Scans the input characters and converts them into tokens.
    
    Args:
        input_chars (str): The source code as a string of characters
        
    Returns:
        list: A list of LexicalToken objects representing the tokens in the source code
        
    The function handles:
    - Identifiers (variables and function names)
    - Numbers (integers)
    - String literals
    - Operators and punctuation
    - Comments
    - Whitespace and newlines
    """
    # Define character sets for different token types
    alpha = 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ'
    digit = '0123456789'
    symbol = '_'
    operator_chars = '+-*<>&.@/:=~|$!#%^_[]{}\"?'
    punctuations = '();,'
    newline_char = '\n'

    # Initialize data structures for token processing
    token_list = []      # Stores the token values
    type_tags = []       # Stores the token categories
    line_indices = []    # Stores the line numbers
    
    index = 0
    buffer = ''
    current_line = 1
    
    try:
        while index < len(input_chars):
            ch = input_chars[index]

            # Process identifiers (variables, function names)
            if ch in alpha:
                buffer += ch
                index += 1
                while index < len(input_chars) and (input_chars[index] in alpha or input_chars[index] in digit or input_chars[index] == symbol):
                    buffer += input_chars[index]
                    index += 1
                token_list.append(buffer)
                type_tags.append('<IDENTIFIER>')
                line_indices.append(current_line)
                buffer = ''

            # Process integers and invalid number formats
            elif ch in digit:
                buffer += ch
                index += 1
                while index < len(input_chars): 
                    if input_chars[index] in digit:
                        buffer += input_chars[index]
                        index += 1
                    elif input_chars[index] in alpha:
                        buffer += input_chars[index]
                        index += 1
                    else:
                        break
                token_list.append(buffer)
                line_indices.append(current_line)
                try:
                    int(buffer)
                    type_tags.append('<INTEGER>')
                except:
                    type_tags.append('<INVALID>')
                buffer = ''

            # Skip comments (lines starting with //)
            elif ch == '/' and index + 1 < len(input_chars) and input_chars[index + 1] == '/':
                buffer += ch + input_chars[index + 1]
                index += 2
                while index < len(input_chars) and input_chars[index] != newline_char:
                    buffer += input_chars[index]
                    index += 1
                token_list.append(buffer)
                type_tags.append('<DELETE>')
                line_indices.append(current_line)
                buffer = ''

            # Handle string literals (enclosed in single quotes)
            elif ch == "'":
                buffer += ch
                index += 1
                while index < len(input_chars):
                    if input_chars[index] == newline_char:
                        current_line += 1
                    if input_chars[index] == "'":
                        buffer += input_chars[index]
                        index += 1
                        break
                    buffer += input_chars[index]
                    index += 1
                if len(buffer) == 1 or buffer[-1] != "'":
                    print("Error: Unclosed string literal.")
                    exit(1)
                token_list.append(buffer)
                type_tags.append('<STRING>')
                line_indices.append(current_line)
                buffer = ''

            # Handle punctuation marks
            elif ch in punctuations:
                buffer = ch
                token_list.append(buffer)
                type_tags.append(buffer)
                line_indices.append(current_line)
                buffer = ''
                index += 1

            # Handle whitespace and tabs
            elif ch in [' ', '\t']:
                buffer = ch
                index += 1
                while index < len(input_chars) and input_chars[index] in [' ', '\t']:
                    buffer += input_chars[index]
                    index += 1
                token_list.append(buffer)
                type_tags.append('<DELETE>')
                line_indices.append(current_line)
                buffer = ''

            # Handle newline characters
            elif ch == newline_char:
                token_list.append(newline_char)
                type_tags.append('<DELETE>')
                line_indices.append(current_line)
                current_line += 1
                index += 1

            # Handle operators
            elif ch in operator_chars:
                while index < len(input_chars) and input_chars[index] in operator_chars:
                    # Avoid mistaking comment slashes as operators
                    if input_chars[index] == '/' and index + 1 < len(input_chars) and input_chars[index + 1] == '/':
                        break
                    buffer += input_chars[index]
                    index += 1
                token_list.append(buffer)
                type_tags.append('<OPERATOR>')
                line_indices.append(current_line)
                buffer = ''

            # Handle unexpected characters
            else:
                print(f"Error: Unknown character '{ch}' at index {index}")
                exit(1)

    except IndexError:
        pass

    # Convert token information into LexicalToken objects
    processed_tokens = []
    total = len(token_list)
    for idx in range(total):
        token_obj = LexicalToken(token_list[idx], type_tags[idx], line_indices[idx])
        if idx == 0:
            token_obj.mark_as_first()
        elif idx == total - 1:
            if token_list[idx] == newline_char:
                processed_tokens[-1].mark_as_last()
                continue
            token_obj.mark_as_last()
        processed_tokens.append(token_obj)

    return processed_tokens
