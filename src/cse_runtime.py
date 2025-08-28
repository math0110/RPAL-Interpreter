"""
This module implements the Control Stack Environment (CSE) Machine for executing RPAL programs.
The CSE machine is responsible for:
1. Generating control structures from the standardized tree
2. Managing the execution environment
3. Implementing built-in functions
4. Handling variable scoping and bindings
"""

from src.standardize_tree import transform_to_standard_form
from src.tree_node import TreeNode
from src.scope_manager import Scope
from src.custom_stack import CustomStack
from src.runtime_entities import *

# Global variables for CSE machine state
control_structures = []  # Stores all control structures
count = 0               # Counter for generating unique indices
control = []           # Current control structure being executed
stack = CustomStack("CSE")  # Stack for the CSE machine
environments = [Scope(0, None)]  # List of all environments
current_environment = 0  # Index of current environment

# List of built-in functions available in RPAL
builtInFunctions = [
    "Order", "Print", "print", "Conc", "Stern", "Stem",
    "Isinteger", "Istruthvalue", "Isstring", "Istuple",
    "Isfunction", "ItoS"
]
is_print_used = False  # Flag to track if Print function is used

def generate_control_structure(root, i):
    """
    Generates control structures from the standardized tree.
    
    Args:
        root (TreeNode): The root node of the standardized tree
        i (int): Index for the current control structure
    """
    global count
    
    while(len(control_structures) <= i):
        control_structures.append([])

    # When lambda is encountered, we have to generate a new control structure.
    if (root.label == "lambda"):
        count += 1
        left_child = root.descendants[0]
        if (left_child.label == ","):
            temp = LambdaClosure(count)
            
            x = ""
            for child in left_child.descendants:
                x += child.label[4:-1] + ","
            x = x[:-1]
            
            temp.bounded_variable = x
            control_structures[i].append(temp)
        else:
            temp = LambdaClosure(count)
            temp.bounded_variable = left_child.label[4:-1]
            control_structures[i].append(temp)

        for child in root.descendants[1:]:
            generate_control_structure(child, count)

    # Handle conditional expressions
    elif (root.label == "->"):
        count += 1
        temp = DeltaNode(count)
        control_structures[i].append(temp)
        generate_control_structure(root.descendants[1], count)
        count += 1
        temp = DeltaNode(count)
        control_structures[i].append(temp)
        generate_control_structure(root.descendants[2], count)
        control_structures[i].append("beta")
        generate_control_structure(root.descendants[0], i)

    # Handle tuple expressions
    elif (root.label == "tau"):
        n = len(root.descendants)
        temp = TupleNode(n)
        control_structures[i].append(temp)
        for child in root.descendants:
            generate_control_structure(child, i)

    # Handle other expressions
    else:
        control_structures[i].append(root.label)
        for child in root.descendants:
            generate_control_structure(child, i)

def lookup(name):
    """
    Looks up a value in the current environment.
    Handles different types of values (integers, strings, identifiers).
    
    Args:
        name (str): The name to look up, in format <TYPE:value>
        
    Returns:
        The value associated with the name
        
    Raises:
        SystemExit: If an undeclared identifier is encountered
    """
    name = name[1:-1]
    info = name.split(":")
    
    if (len(info) == 1):
        label = info[0]
    else:
        data_type = info[0]
        label = info[1]
    
        if data_type == "INT":
            return int(label)
        
        # The rpal.exe program detects srings only when they begin with ' and end with '.
        # Our code must emulate this behaviour.
        elif data_type == "STR":
            return label.strip("'")
        elif data_type == "ID":
            if (label in builtInFunctions):
                return label
            else:
                try:
                    label = environments[current_environment].bindings[label]
                except KeyError:
                    print("Undeclared Identifier: " + label)
                    exit(1)
                else:
                    return label
            
    if label == "Y*":
        return "Y*"
    elif label == "nil":
        return ()
    elif label == "true":
        return True
    elif label == "false":
        return False

def built_in(function, argument):
    """
    Implements built-in RPAL functions.
    
    Args:
        function (str): Name of the built-in function
        argument: The argument to the function
    """
    global is_print_used
    
    # The Order function returns the length of a tuple.  
    if (function == "Order"):
        order = len(argument)
        stack.push(order)

    # Print: Outputs values to the console
    elif (function == "Print" or function == "print"):
        is_print_used = True
        
        # If there are escape characters in the string, we need to format it properly.
        if type(argument) == str:
            if "\\n" in argument:
                argument = argument.replace("\\n", "\n")
            if "\\t" in argument:
                argument = argument.replace("\\t", "\t")
        stack.push(argument)

    # String operations
    elif (function == "Conc"):  # Concatenate strings
        stack_symbol = stack.pop()
        control.pop()
        temp = argument + stack_symbol
        stack.push(temp)

    # The Stern function returns the string without the first letter.
    elif (function == "Stern"):
        stack.push(argument[1:])

    # The Stem function returns the first letter of the given string.
    elif (function == "Stem"):
        stack.push(argument[0])

    # The Isinteger function checks if the given argument is an integer.
    elif (function == "Isinteger"):
        if (type(argument) == int):
            stack.push(True)
        else:
            stack.push(False)

    # The Istruthvalue function checks if the given argument is a boolean value.               
    elif (function == "Istruthvalue"):
        if (type(argument) == bool):
            stack.push(True)
        else:
            stack.push(False)

    # The Isstring function checks if the given argument is a string.
    elif (function == "Isstring"):
        if (type(argument) == str):
            stack.push(True)
        else:
            stack.push(False)

    # The Istuple function checks if the given argument is a tuple.
    elif (function == "Istuple"):
        if (type(argument) == tuple):
            stack.push(True)
        else:
            stack.push(False)

    # The Isfunction function checks if the given argument is a built-in function.
    elif (function == "Isfunction"):
        if (argument in builtInFunctions):
            return True
        else:
            False
    
    # The ItoS function converts integers to strings.        
    elif (function == "ItoS"):
        if (type(argument) == int):
            stack.push(str(argument))
        else:
            print("Error: ItoS function can only accept integers.")
            exit()

def apply_rules():
    """
    Applies CSE machine rules to execute the program.
    Implements the core execution logic of the RPAL interpreter.
    """
    op = ["+", "-", "*", "/", "**", "gr", "ge", "ls", "le", "eq", "ne", "or", "&", "aug"]
    uop = ["neg", "not"]

    global control
    global current_environment

    while(len(control) > 0):
        symbol = control.pop()

        # Rule 1: Handle values and identifiers
        if type(symbol) == str and (symbol[0] == "<" and symbol[-1] == ">"):
            stack.push(lookup(symbol))

        # Rule 2: Handle lambda closures
        elif type(symbol) == LambdaClosure:
            temp = LambdaClosure(symbol.index)
            temp.bounded_variable = symbol.bounded_variable
            temp.environment = current_environment
            stack.push(temp)

        # Rule 4: Handle function application
        elif (symbol == "gamma"):
            stack_symbol_1 = stack.pop()
            stack_symbol_2 = stack.pop()

            if (type(stack_symbol_1) == LambdaClosure):
                current_environment = len(environments)
                
                lambda_index = stack_symbol_1.index
                bounded_variable = stack_symbol_1.bounded_variable
                parent_environment_index = stack_symbol_1.environment

                parent = environments[parent_environment_index]
                child = Scope(current_environment, parent)
                parent.attach_child_scope(child)
                environments.append(child)

                # Rule 11: Handle multiple parameters
                variable_list = bounded_variable.split(",")
                
                if (len(variable_list) > 1):
                    for i in range(len(variable_list)):
                        child.bind_variable(variable_list[i], stack_symbol_2[i])
                else:
                    child.bind_variable(bounded_variable, stack_symbol_2)

                stack.push(child.name)
                control.append(child.name)
                control += control_structures[lambda_index]

            # Rule 10: Handle tuple indexing
            elif (type(stack_symbol_1) == tuple):
                stack.push(stack_symbol_1[stack_symbol_2 - 1])

            # Rule 12: Handle Y* combinator
            elif (stack_symbol_1 == "Y*"):
                temp = EtaClosure(stack_symbol_2.index)
                temp.bounded_variable = stack_symbol_2.bounded_variable
                temp.environment = stack_symbol_2.environment
                stack.push(temp)

            # Rule 13: Handle eta closures
            elif (type(stack_symbol_1) == EtaClosure):
                temp = LambdaClosure(stack_symbol_1.index)
                temp.bounded_variable = stack_symbol_1.bounded_variable
                temp.environment = stack_symbol_1.environment
                
                control.append("gamma")
                control.append("gamma")
                stack.push(stack_symbol_2)
                stack.push(stack_symbol_1)
                stack.push(temp)

            # Handle built-in functions
            elif stack_symbol_1 in builtInFunctions:
                built_in(stack_symbol_1, stack_symbol_2)
              
        # Rule 5: Handle environment markers
        elif type(symbol) == str and (symbol[0:2] == "e_"):
            stack_symbol = stack.pop()
            stack.pop()
            
            if (current_environment != 0):
                for element in reversed(stack):
                    if (type(element) == str and element[0:2] == "e_"):
                        current_environment = int(element[2:])
                        break
            stack.push(stack_symbol)

        # Rule 6: Handle binary operators
        elif (symbol in op):
            rand_1 = stack.pop()
            rand_2 = stack.pop()
            if (symbol == "+"): 
                stack.push(rand_1 + rand_2)
            elif (symbol == "-"):
                stack.push(rand_1 - rand_2)
            elif (symbol == "*"):
                stack.push(rand_1 * rand_2)
            elif (symbol == "/"):
                stack.push(rand_1 // rand_2)
            elif (symbol == "**"):
                stack.push(rand_1 ** rand_2)
            elif (symbol == "gr"):
                stack.push(rand_1 > rand_2)
            elif (symbol == "ge"):
                stack.push(rand_1 >= rand_2)
            elif (symbol == "ls"):
                stack.push(rand_1 < rand_2)
            elif (symbol == "le"):
                stack.push(rand_1 <= rand_2)
            elif (symbol == "eq"):
                stack.push(rand_1 == rand_2)
            elif (symbol == "ne"):
                stack.push(rand_1 != rand_2)
            elif (symbol == "or"):
                stack.push(rand_1 or rand_2)
            elif (symbol == "&"):
                stack.push(rand_1 and rand_2)
            elif (symbol == "aug"):
                if (type(rand_2) == tuple):
                    stack.push(rand_1 + rand_2)
                else:
                    stack.push(rand_1 + (rand_2,))

        # Rule 7: Handle unary operators
        elif (symbol in uop):
            rand = stack.pop()
            if (symbol == "not"):
                stack.push(not rand)
            elif (symbol == "neg"):
                stack.push(-rand)

        # Rule 8: Handle conditional execution
        elif (symbol == "beta"):
            B = stack.pop()
            else_part = control.pop()
            then_part = control.pop()
            if (B):
                control += control_structures[then_part.index]
            else:
                control += control_structures[else_part.index]

        # Rule 9: Handle tuple construction
        elif type(symbol) == TupleNode:
            n = symbol.index
            tau_list = []
            for i in range(n):
                tau_list.append(stack.pop())
            tau_tuple = tuple(tau_list)
            stack.push(tau_tuple)

        elif (symbol == "Y*"):
            stack.push(symbol)

    # Lambda expression becomes a lambda closure when its environment is determined.
    if type(stack[0]) == LambdaClosure:
        stack[0] = "[lambda closure: " + str(stack[0].bounded_variable) + ": " + str(stack[0].index) + "]"
         
    # Format output for tuples
    if type(stack[0]) == tuple:          
        # The rpal.exe program prints the boolean values in lowercase. Our code must emulate this behaviour. 
        for i in range(len(stack[0])):
            if type(stack[0][i]) == bool:
                stack[0] = list(stack[0])
                stack[0][i] = str(stack[0][i]).lower()
                stack[0] = tuple(stack[0])
                
        # The rpal.exe program does not print the comma when there is only one element in the tuple.
        # Our code must emulate this behaviour.  
        if len(stack[0]) == 1:
            stack[0] = "(" + str(stack[0][0]) + ")"
        
        # The rpal.exe program does not print inverted commas when an element in the tuple is a string.
        # Our code must emulate this behaviour too. 
        else: 
            if any(type(element) == str for element in stack[0]):
                temp = "("
                for element in stack[0]:
                    temp += str(element) + ", "
                temp = temp[:-2] + ")"
                stack[0] = temp
                
    # The rpal.exe program prints the boolean values in lowercase. Our code must emulate this behaviour.    
    if stack[0] == True or stack[0] == False:
        stack[0] = str(stack[0]).lower()

def get_result(file_name):
    """
    Main entry point for executing an RPAL program.
    
    Args:
        file_name (str): Path to the RPAL source file
    """
    global control

    # Transform the program to standard form
    st = transform_to_standard_form(file_name)
    
    # Generate control structures
    generate_control_structure(st, 0) 
    
    # Initialize control and stack
    control.append(environments[0].name)
    control += control_structures[0]

    stack.push(environments[0].name)

    # Execute the program
    apply_rules()

    # Print result if Print was used
    if is_print_used:
        print(stack[0])