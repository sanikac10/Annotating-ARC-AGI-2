import os
import sys
from solution_extractor import create_standalone_solution
from problem_ids import problem_ids

def main():
    # Create the output directory if it doesn't exist
    output_dir = "standalone_solutions"
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
        print(f"Created directory: {output_dir}")
    
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
    
    # Generate solutions for each problem ID
    successful = 0
    failed = 0
    
    for problem_id in problem_ids:
        output_filename = os.path.join(output_dir, f"solving_{problem_id}.py")
        print(f"Creating solution for problem {problem_id}...")
        
        standalone = create_standalone_solution(
            problem_id, solvers_content, dsl_content, constants_content, arc_types_content
        )
        
        # Check if the solver was found
        if standalone.startswith("Error:"):
            print(f"  {standalone}")
            failed += 1
            continue
        
        # Write the output file
        with open(output_filename, 'w') as f:
            f.write(standalone)
        
        print(f"  Successfully created {output_filename}")
        successful += 1
    
    # Print summary
    print(f"\nSummary: Successfully generated {successful} solutions, failed to generate {failed} solutions.")
    print(f"Solutions saved in the '{output_dir}' directory.")

if __name__ == "__main__":
    main()