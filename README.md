# RPAL Interpreter

This is an interpreter for the RPAL programming language, implemented in Python.
It performs lexical analysis, parsing, abstract syntax tree generation, standardization, and execution using a CSE machine model.

# 📁 Project Structure

RPAL-PROJECT/
├── myrpal.py # Main script to run the RPAL interpreter with command-line options
├── sample1 # Sample RPAL source file for testing
├── sample2 # Additional test file
├── sample3
├── ...
├── sample10 # Up to sample10 - collection of sample RPAL programs
├── src/
│ ├── tokenizer.py # Performs lexical analysis (turns characters into tokens)
│ ├── screener_module.py # Screens and classifies tokens, removes invalid or unnecessary ones
│ ├── rpal_ast_builder.py # Builds the Abstract Syntax Tree (AST) using recursive descent parsing
│ ├── standardize_tree.py # Converts AST into a standardized form suitable for execution
│ ├── cse_runtime.py # Implements the Control Stack Environment (CSE) Machine to evaluate programs
│ ├── tree_node.py # Defines the TreeNode class used for AST and standardized tree nodes
│ ├── custom_stack.py # Stack data structure used by both parser and CSE machine
│ ├── runtime_entities.py # Defines runtime entities like LambdaClosure, EtaClosure, DeltaNode, TupleNode
│ ├── scope_manager.py # Manages variable scopes and environment bindings during interpretation
│ ├── token_model.py # Defines the Token class used by the tokenizer and screener

# ✅ Requirements

- Python 3.7 or higher

# 🚀 Run the Interpreter

From terminal or command prompt:

$ python myrpal.py [options] <filename>

# 🛠️ Options

-l → Print the raw program
-ast → Print the Abstract Syntax Tree (AST)
-st → Print the standardized tree
(no flags) → Run and print the final result

# 🧪 Examples

$ python myrpal.py sample1
$ python myrpal.py -l sample1
$ python myrpal.py -ast sample1
$ python myrpal.py -st sample1

# 👨‍💻 Author

Written for an academic Programming Languages module to demonstrate parsing, tree transformations, and interpretation of a functional language.
