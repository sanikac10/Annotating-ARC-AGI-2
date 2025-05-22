import streamlit as st
import json
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors
from matplotlib.patches import Rectangle
import os
from datetime import datetime
from utils import run_function

class ARCVisualizer:
    def __init__(self, training_challenges_path="./data/arc-agi_training_challenges.json", 
                 training_solutions_path="./data/arc-agi_training_solutions.json"):
        self.training_challenges_path = training_challenges_path
        self.training_solutions_path = training_solutions_path
        try:
            self.training_challenges_ds, self.training_solutions_ds = self.load_all_training_data()
            self.training_keys = sorted(list(set(list(self.training_challenges_ds.keys()))))
            self.data_loaded = True
            os.makedirs("temp", exist_ok=True)
        except Exception as e:
            st.error(f"Error loading data: {e}")
            self.data_loaded = False
    
    def load_all_training_data(self):
        with open(self.training_challenges_path, "r") as f:
            challenges_ds = json.load(f)
        with open(self.training_solutions_path, "r") as f:
            solutions_ds = json.load(f)
        return challenges_ds, solutions_ds
    
    def get_challenge(self, index):
        if not self.data_loaded:
            return None, None, None
        
        key = self.training_keys[index]
        challenge = self.training_challenges_ds[key]
        solution = self.training_solutions_ds[key]
        return challenge, solution, key
    
    def plot_grid(self, grid, title="", save_path=None, is_input=None, dimensions=None):
        if not grid:
            return None
        
        height = len(grid)
        width = len(grid[0]) if height > 0 else 0
        
        # Create an enhanced title if dimensions and input/output type are provided
        if is_input is not None and dimensions is not None:
            title = f"{title} - {'Input' if is_input else 'Output'} ({height}x{width})"
        
        cmap = plt.cm.tab10
        norm = mcolors.Normalize(vmin=0, vmax=9)
        
        fig, ax = plt.subplots(figsize=(max(4, width/2), max(4, height/2)))
        ax.set_title(title)
        
        for i in range(height):
            for j in range(width):
                color = cmap(norm(grid[i][j]))
                ax.add_patch(Rectangle((j, height-i-1), 1, 1, color=color))
                ax.text(j+0.5, height-i-0.5, str(grid[i][j]), 
                        ha='center', va='center', color='white')
        
        ax.set_xlim(0, width)
        ax.set_ylim(0, height)
        ax.set_aspect('equal')
        
        ax.grid(True, color='black', linewidth=0.5)
        
        ax.set_xticks(np.arange(0, width+1, 1))
        ax.set_yticks(np.arange(0, height+1, 1))
        ax.set_xticklabels([])
        ax.set_yticklabels([])
        
        if save_path:
            plt.savefig(save_path, bbox_inches='tight')
        
        return fig
    
    def save_analysis(self, challenge_id, user_explanation, function_output, user_comments, index):
        os.makedirs("annotations", exist_ok=True)
        filename = f"annotations/{index}.json"
        
        data = {
            "challenge_id": challenge_id,
            "timestamp": datetime.now().strftime("%Y%m%d_%H%M%S"),
            "user_explanation": user_explanation,
            "function_output": function_output,
            "user_comments": user_comments
        }
        
        with open(filename, "w") as f:
            json.dump(data, f, indent=4)
        
        return filename

def main():
    st.title("ARC-AGI-2 Challenge Visualizer")
    
    visualizer = ARCVisualizer()
    
    if not visualizer.data_loaded:
        st.warning("Please ensure ARC-AGI challenge and solution files are in the ./data/ directory.")
        st.stop()
    
    # Initialize session state variables if they don't exist
    if 'user_explanation' not in st.session_state:
        st.session_state.user_explanation = ""
    if 'function_output' not in st.session_state:
        st.session_state.function_output = ""
    if 'user_comments' not in st.session_state:
        st.session_state.user_comments = ""
    if 'current_challenge_index' not in st.session_state:
        st.session_state.current_challenge_index = 0
    
    num_challenges = len(visualizer.training_keys)
    challenge_index = st.number_input("Challenge Index", 
                                     min_value=0, 
                                     max_value=num_challenges-1, 
                                     value=0)
    
    # Clear temp directory when switching to a new challenge
    if challenge_index != st.session_state.current_challenge_index:
        if os.path.exists("temp"):
            for f in os.listdir("temp"):
                if f.endswith('.png'):
                    os.remove(os.path.join("temp", f))
        st.session_state.current_challenge_index = challenge_index
    
    challenge, solution, challenge_id = visualizer.get_challenge(challenge_index)
    
    if challenge and solution:
        st.subheader(f"Challenge ID: {challenge_id}")
        
        # Create main columns for the split layout
        col_visualizations, col_inputs = st.columns([3, 2])
        
        with col_visualizations:
            st.header("Challenge Visualizations")
            
            # Training Examples
            st.subheader("Training Examples")
            train_data = challenge.get("train", [])
            
            for i, example in enumerate(train_data):
                sub_col1, sub_col2 = st.columns(2)
                
                with sub_col1:
                    input_grid = example.get("input")
                    grid_height = len(input_grid)
                    grid_width = len(input_grid[0]) if grid_height > 0 else 0
                    st.markdown(f"**Example {i+1} Input ({grid_height}x{grid_width})**")
                    input_fig = visualizer.plot_grid(
                        input_grid, 
                        title=f"Example {i+1}",
                        save_path=f"temp/challenge_example_{i+1}.png",
                        is_input=True,
                        dimensions=True
                    )
                    if input_fig:
                        st.pyplot(input_fig)
                
                with sub_col2:
                    output_grid = example.get("output")
                    grid_height = len(output_grid)
                    grid_width = len(output_grid[0]) if grid_height > 0 else 0
                    st.markdown(f"**Example {i+1} Output ({grid_height}x{grid_width})**")
                    output_fig = visualizer.plot_grid(
                        output_grid, 
                        title=f"Example {i+1}",
                        save_path=f"temp/solution_example_{i+1}.png",
                        is_input=False,
                        dimensions=True
                    )
                    if output_fig:
                        st.pyplot(output_fig)
            
            # Test Example
            st.subheader("Test Example")
            test_data = challenge.get("test", [])
            
            for i, test in enumerate(test_data):
                sub_col1, sub_col2 = st.columns(2)
                
                with sub_col1:
                    test_input = test.get("input")
                    grid_height = len(test_input)
                    grid_width = len(test_input[0]) if grid_height > 0 else 0
                    st.markdown(f"**Test Input ({grid_height}x{grid_width})**")
                    test_fig = visualizer.plot_grid(
                        test_input, 
                        title="Test",
                        save_path=f"temp/challenge_example_3.png",
                        is_input=True,
                        dimensions=True
                    )
                    if test_fig:
                        st.pyplot(test_fig)
                
                with sub_col2:
                    test_output = solution[i]
                    grid_height = len(test_output)
                    grid_width = len(test_output[0]) if grid_height > 0 else 0
                    st.markdown(f"**Test Output ({grid_height}x{grid_width})**")
                    sol_fig = visualizer.plot_grid(
                        test_output, 
                        title="Test",
                        save_path=f"temp/solution_example_3.png",
                        is_input=False,
                        dimensions=True
                    )
                    if sol_fig:
                        st.pyplot(sol_fig)
        
        with col_inputs:
            st.header("Analysis")
            
            # User Explanation
            st.subheader("Your Explanation")
            user_explanation = st.text_area("Explain the pattern", 
                                          value=st.session_state.user_explanation,
                                          height=150)
            st.session_state.user_explanation = user_explanation
            
            # Get all image paths from the temp directory by scanning it
            image_paths = []
            if os.path.exists("temp"):
                image_paths = [os.path.join("temp", f) for f in os.listdir("temp") if f.endswith('.png')]
                image_paths.sort()  # Sort the paths for consistency
            
            # Run Function Button
            if st.button("Run Function"):
                if user_explanation:
                    st.session_state.function_output = run_function(user_explanation, challenge_id, image_paths)
                else:
                    st.warning("Please enter an explanation first")
            
            # Function Output
            st.subheader("Function Output")
            if st.session_state.function_output:
                st.text_area("Result", value=st.session_state.function_output, height=200, disabled=True)
            else:
                st.info("Click 'Run Function' to process your explanation")
            
            # Comments
            st.subheader("Comments")
            user_comments = st.text_area("Additional comments or observations", 
                                        value=st.session_state.user_comments,
                                        height=100)
            st.session_state.user_comments = user_comments
            
            # Save Button
            if st.button("Submit & Save"):
                if user_explanation:
                    saved_file = visualizer.save_analysis(
                        challenge_id, 
                        st.session_state.user_explanation, 
                        st.session_state.function_output, 
                        st.session_state.user_comments,
                        challenge_index
                    )
                    st.success(f"Analysis saved to {saved_file}")
                else:
                    st.warning("Please provide an explanation before saving")

if __name__ == "__main__":
    main()