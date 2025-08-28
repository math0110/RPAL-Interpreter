# entry_point.py

"""
Main execution file for the RPAL interpreter.

This module serves as the entry point for the RPAL interpreter, providing a command-line
interface to execute RPAL programs with various options for debugging and visualization.

Usage:
    python myrpal.py [-l] [-ast] [-st] filename

Options:
    -l      : Print the source code
    -ast    : Print the Abstract Syntax Tree
    -st     : Print the Standard Tree

Note:
    Must be run via terminal. Not intended for IDE execution.
"""

import sys
from src.rpal_ast_builder import parse_rpal_program
from src.tree_node import print_tree_preorder
from src.standardize_tree import transform_to_standard_form, standardize_subtree
from src.cse_runtime import get_result

def show_usage():
    """
    Displays the usage instructions for the RPAL interpreter.
    Called when incorrect command-line arguments are provided.
    """
    print("Usage:\n  python myrpal.py [-l] [-ast] [-st] filename")

def main():
    """
    Main entry point for the RPAL interpreter.
    
    The function:
    1. Parses command-line arguments
    2. Validates the input file and options
    3. Executes the requested operations:
       - Print source code (-l)
       - Print AST (-ast)
       - Print Standard Tree (-st)
       - Execute program (default)
    
    Raises:
        SystemExit: If incorrect arguments are provided or file is not found
    """
    args = sys.argv

    if len(args) < 2:
        show_usage()
        sys.exit(1)

    flags = args[1:-1]
    filename = args[-1]

    if not flags:
        # Default: Execute the program
        get_result(filename)
    else:
        # Validate flags
        if any(opt not in ("-l", "-ast", "-st") for opt in flags):
            show_usage()
            sys.exit(1)

        # Print source code if requested
        if "-l" in flags:
            try:
                with open(filename, "r") as source:
                    print(source.read())
                print()
            except FileNotFoundError:
                print(f"Error: File '{filename}' not found.")
                sys.exit(1)

        # Print AST if requested
        if "-ast" in flags:
            ast = parse_rpal_program(filename)
            print_tree_preorder(ast)
            print()

            # Print Standard Tree if both -ast and -st are requested
            if "-st" in flags:
                st = standardize_subtree(ast)
                print_tree_preorder(st)
                print()
                sys.exit()

        # Print Standard Tree if only -st is requested
        elif "-st" in flags:
            st = transform_to_standard_form(filename)
            print_tree_preorder(st)
            print()
            sys.exit()

if __name__ == "__main__":
    main()
