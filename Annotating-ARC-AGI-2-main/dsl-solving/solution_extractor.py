import re
import ast
from typing import Set, Dict, List, Any

def extract_solver_function(solvers_content: str, problem_id: str) -> str:
    """Extract the solver function for a specific problem ID."""
    pattern = rf"def solve_{problem_id}\([^)]*\):(?:(?!\ndef ).)*"
    match = re.search(pattern, solvers_content, re.DOTALL)
    if not match:
        return ""
    return match.group(0)

def extract_function_calls(function_code: str) -> Set[str]:
    """Extract all function calls from a function code."""
    function_calls = set()
    
    # Parse the function code
    tree = ast.parse(function_code)
    
    # Find all function calls
    for node in ast.walk(tree):
        if isinstance(node, ast.Call) and isinstance(node.func, ast.Name):
            function_calls.add(node.func.id)
    
    return function_calls

def extract_identifiers(function_code: str) -> Set[str]:
    """Extract all identifiers (variables, constants) from function code."""
    identifiers = set()
    
    # Parse the function code
    tree = ast.parse(function_code)
    
    # Find all identifiers
    for node in ast.walk(tree):
        if isinstance(node, ast.Name):
            # Exclude the parameter name (typically 'I' in these functions)
            if not (isinstance(node.ctx, ast.Param)):
                identifiers.add(node.id)
    
    return identifiers

def extract_dsl_functions(dsl_content: str, function_names: Set[str]) -> Dict[str, str]:
    """Extract DSL function definitions based on used function names."""
    extracted_functions = {}
    
    for func_name in function_names:
        pattern = rf"def {func_name}\([^)]*\)(?:\s*->.*?)?:(?:(?!\ndef ).)*"
        match = re.search(pattern, dsl_content, re.DOTALL)
        if match:
            extracted_functions[func_name] = match.group(0)
    
    return extracted_functions

def extract_constants(constants_content: str, constant_names: Set[str]) -> Dict[str, str]:
    """Extract constants based on used constant names."""
    extracted_constants = {}
    lines = constants_content.split('\n')
    
    for line in lines:
        for const_name in constant_names:
            pattern = rf"^{const_name}\s*=\s*.*$"
            if re.match(pattern, line):
                extracted_constants[const_name] = line
                break
    
    return extracted_constants

def extract_recursive_dependencies(dsl_content: str, functions: Dict[str, str]) -> Dict[str, str]:
    """Find recursive dependencies in the DSL functions."""
    all_functions = functions.copy()
    
    # Keep checking for new dependencies until no more are found
    while True:
        initial_count = len(all_functions)
        
        for func_code in list(all_functions.values()):
            func_calls = extract_function_calls(func_code)
            
            for call in func_calls:
                if call not in all_functions:
                    pattern = rf"def {call}\([^)]*\)(?:\s*->.*?)?:(?:(?!\ndef ).)*"
                    match = re.search(pattern, dsl_content, re.DOTALL)
                    if match:
                        all_functions[call] = match.group(0)
        
        if len(all_functions) == initial_count:
            # No new functions were added
            break
    
    return all_functions

def extract_imports(content: str, needed_modules: Set[str] = None) -> List[str]:
    """
    Extract import statements from Python code.
    If needed_modules is provided, only extract imports for those modules.
    """
    imports = []
    tree = ast.parse(content)
    
    for node in ast.walk(tree):
        if isinstance(node, (ast.Import, ast.ImportFrom)):
            if needed_modules is None:
                # Include all imports if no filter is provided
                imports.append(ast.unparse(node))
            else:
                # Filter imports based on needed modules
                if isinstance(node, ast.ImportFrom):
                    # For from X import Y statements
                    module = node.module
                    names = [n.name for n in node.names]
                    if module in needed_modules or any(name in needed_modules for name in names):
                        imports.append(ast.unparse(node))
                else:
                    # For import X statements
                    names = [n.name for n in node.names]
                    if any(name in needed_modules for name in names):
                        imports.append(ast.unparse(node))
    
    return imports

def extract_type_definitions(arc_types_content: str, dsl_functions: Dict[str, str]) -> List[str]:
    """Extract type definitions needed for DSL functions."""
    all_types = set()
    
    # Parse the DSL functions to find type annotations
    for func_code in dsl_functions.values():
        # Look for type annotations in function signatures
        signature_pattern = r"def\s+\w+\s*\([^)]*\)\s*->\s*([^:]+):"
        param_pattern = r"(\w+)\s*:\s*([^,=)]+)"
        
        # Find return type annotations
        return_matches = re.findall(signature_pattern, func_code)
        for match in return_matches:
            type_names = re.findall(r"(\w+)(?:\[[\w, ]*\])?", match)
            all_types.update(type_names)
        
        # Find parameter type annotations
        param_matches = re.findall(param_pattern, func_code)
        for _, type_name in param_matches:
            type_names = re.findall(r"(\w+)(?:\[[\w, ]*\])?", type_name)
            all_types.update(type_names)
    
    # Also look for isinstance() checks that might reference types
    isinstance_pattern = r"isinstance\s*\([^,]+,\s*(\w+)\)"
    for func_code in dsl_functions.values():
        isinstance_matches = re.findall(isinstance_pattern, func_code)
        all_types.update(isinstance_matches)
    
    # Parse the arc_types file to get available type definitions
    type_def_pattern = r"^(\w+)\s*=\s*"
    available_types = set()
    lines = arc_types_content.split('\n')
    for line in lines:
        match = re.match(type_def_pattern, line)
        if match:
            available_types.add(match.group(1))
    
    # Find the types that are actually defined in arc_types.py
    types_to_extract = all_types.intersection(available_types)
    
    # Track dependencies between types
    type_dependencies = {}
    for line in lines:
        for type_name in types_to_extract:
            if re.match(rf"{type_name}\s*=", line):
                # Find types that this type references
                referenced_types = re.findall(r"(\w+)(?:\[[\w, ]*\])?", line)
                type_dependencies[type_name] = [t for t in referenced_types if t in available_types and t != type_name]
    
    # Resolve all transitive dependencies
    all_needed_types = set(types_to_extract)
    prev_size = 0
    while prev_size != len(all_needed_types):
        prev_size = len(all_needed_types)
        for type_name in list(all_needed_types):
            if type_name in type_dependencies:
                all_needed_types.update(type_dependencies[type_name])
    
    # Extract relevant type definitions and imports
    type_defs = []
    for line in lines:
        for type_name in all_needed_types:
            if re.match(rf"{type_name}\s*=", line):
                type_defs.append(line)
                break
    
    # Parse the tree to properly extract imports
    tree = ast.parse(arc_types_content)
    import_nodes = [node for node in ast.walk(tree) if isinstance(node, (ast.Import, ast.ImportFrom))]
    
    # Filter to only include imports needed for the types we're using
    needed_imports = []
    for node in import_nodes:
        if isinstance(node, ast.ImportFrom):
            # For 'from x import y' statements
            module = node.module
            names = [n.name for n in node.names]
            # Only include if it's importing types we need
            if any(name in all_needed_types for name in names) or module == 'typing':
                needed_imports.append(ast.unparse(node))
        else:
            # For 'import x' statements, always include
            needed_imports.append(ast.unparse(node))
    
    return needed_imports + type_defs

def analyze_constant_usage(dsl_functions: Dict[str, str], solver_code: str) -> Set[str]:
    """Analyze which constants are actually used in the functions."""
    all_code = solver_code + "\n" + "\n".join(dsl_functions.values())
    
    # Identify all variable names used in the code
    used_names = set()
    tree = ast.parse(all_code)
    
    for node in ast.walk(tree):
        if isinstance(node, ast.Name) and isinstance(node.ctx, ast.Load):
            used_names.add(node.id)
    
    return used_names

def create_standalone_solution(
    problem_id: str,
    solvers_content: str,
    dsl_content: str,
    constants_content: str,
    arc_types_content: str
) -> str:
    """Create a standalone solution file for a specific problem ID."""
    # Extract the solver function
    solver_function = extract_solver_function(solvers_content, problem_id)
    if not solver_function:
        return f"Error: Solver function for {problem_id} not found."
    
    # Extract function calls from the solver
    function_calls = extract_function_calls(solver_function)
    
    # Extract the DSL functions
    dsl_functions = extract_dsl_functions(dsl_content, function_calls)
    
    # Find recursive dependencies in DSL functions
    all_dsl_functions = extract_recursive_dependencies(dsl_content, dsl_functions)
    
    # Find all identifiers actually used in the solver and DSL functions
    used_identifiers = analyze_constant_usage(all_dsl_functions, solver_function)
    
    # Extract only the constants that are actually used
    constants = extract_constants(constants_content, used_identifiers)
    
    # Start with the complete arc_types.py content
    standalone_content = ["# Standalone solution for ARC-AGI problem " + problem_id]
    standalone_content.append("\n# Complete arc_types.py content")
    standalone_content.append("'''\nThe following is the complete content of arc_types.py:\n'''")
    standalone_content.append(arc_types_content)
    
    # Include constants if we have any
    if constants:
        standalone_content.append("\n# Constants")
        for const_line in constants.values():
            standalone_content.append(const_line)
    
    standalone_content.append("\n# DSL functions")
    for func_code in all_dsl_functions.values():
        standalone_content.append(func_code)
    
    standalone_content.append("\n# Solver function")
    standalone_content.append(solver_function)
    
    # Add a main section to demonstrate usage
    standalone_content.append("\n# Example usage")
    standalone_content.append("if __name__ == '__main__':")
    standalone_content.append("    # Example input grid - replace with actual test data")
    standalone_content.append("    test_input = ((0, 0), (0, 0))")
    standalone_content.append(f"    result = solve_{problem_id}(test_input)")
    standalone_content.append("    print(f\"Input: {test_input}\")")
    standalone_content.append("    print(f\"Output: {result}\")")
    
    return "\n".join(standalone_content)

# Complete example showing the usage
if __name__ == "__main__":
    import sys
    import os
    
    if len(sys.argv) < 2:
        print("Usage: python solution_extractor.py <problem_id>")
        sys.exit(1)
    
    problem_id = sys.argv[1]
    
    # Check if the input files exist
    required_files = ['solvers.py', 'dsl.py', 'constants.py', 'arc_types.py']
    for file in required_files:
        if not os.path.exists(file):
            print(f"Error: Required file {file} not found.")
            sys.exit(1)
    
    # Read the input files
    with open('solvers.py', 'r') as f:
        solvers_content = f.read()
    with open('dsl.py', 'r') as f:
        dsl_content = f.read()
    with open('constants.py', 'r') as f:
        constants_content = f.read()
    with open('arc_types.py', 'r') as f:
        arc_types_content = f.read()
    
    # Create the standalone solution
    output_filename = f"solving_{problem_id}.py"
    print(f"Creating standalone solution for problem {problem_id}...")
    
    standalone = create_standalone_solution(
        problem_id, solvers_content, dsl_content, constants_content, arc_types_content
    )
    
    # Check if the solver was found
    if standalone.startswith("Error:"):
        print(standalone)
        sys.exit(1)
    
    # Write the output file
    with open(output_filename, 'w') as f:
        f.write(standalone)
    
    print(f"Successfully created {output_filename}")
    
    # Show what functions and imports were included
    included_functions = re.findall(r"def (\w+)\(", standalone)
    included_imports = re.findall(r"from (\w+) import", standalone)
    
    print(f"\nIncluded {len(included_functions)} functions:")
    for func in included_functions:
        print(f"- {func}")
    
    if included_imports:
        print(f"\nIncluded imports from modules:")
        for module in included_imports:
            print(f"- {module}")
            
    print("\nDone!")