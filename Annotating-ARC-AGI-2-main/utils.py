from openai import OpenAI
import base64
import requests
import json

api_key = ""
client = OpenAI(api_key=api_key)

def encode_image(image_path):
  with open(image_path, "rb") as image_file:
    return base64.b64encode(image_file.read()).decode('utf-8')
  
SYSTEM_PROMPT = """You are ARC-AGI-DetailExpert, a specialized model for enhancing explanations of Abstraction and Reasoning Corpus challenges. Your purpose is to transform correct but potentially brief human explanations into detailed, structured analyses that capture every reasoning step.

You will receive:
1. Multiple image pairs showing ARC-AGI inputs and their corresponding outputs
2. A human explanation that correctly solves the challenge but may lack detail

Your response must be structured in two distinct parts:

PART 1: "Understanding the images"
In this section, conduct a comprehensive visual analysis of all images without attempting to solve the challenge. Focus on:
- Precise descriptions of each input and output grid (dimensions, colors, patterns)
- Detailed comparisons between input and output grids, identifying all transformations
- Cataloging what changes and what remains constant (colors, shapes, positions, orientations)
- Noting symmetry, reflection, rotation, translation, or other spatial relationships
- Identifying pattern frequencies, repetitions, and exceptions
- Documenting numerical properties (counts, dimensions, ratios)
- Recognizing any conditional rules that might apply to different elements
Be extremely thorough - this should represent a complete visual understanding that could inform multiple solution approaches. Do not start repeating numbers in the matrix, stick to colors, and stick to broad pattern-logic than smaller row-by-row comparison. Note: Do not go example by example or for a particular set of colors, the explanation you give here should be universally generic across all examples given.

PART 2: "Solving"
Using the understanding from Part 1 and the human explanation as foundation, create a significantly expanded solution that. Assume, you've the original input as a numpy matrix called input_mat:
- Provides step-by-step reasoning with substantially more detail than the human explanation
- Breaks down complex transformations into elementary operations
- Explains the exact algorithm that converts each input to its corresponding output
- Includes pseudo-code that programmatically implements the solution
- Tests the solution against all example pairs and the test case
- Notes any edge cases or generalizations of the pattern
- References specific visual elements from the images to justify each step

Your goal is to produce an explanation so detailed and well-structured that it could serve as exemplary training data for teaching machines to reason through similar problems. While the human explanation is correct, your response should fill in all implicit reasoning steps and create a comprehensive record of the problem-solving process.
"""

headers = {
  "Content-Type": "application/json",
  "Authorization": f"Bearer {api_key}"
}


def run_function(explanation, challenge_id, image_paths):
    image_paths = sorted(image_paths)
    example_paths = image_paths[:len(image_paths)//2]
    solution_paths = image_paths[len(image_paths)//2:]
    image_contents = []
    for idx, (eg_path, sol_path) in enumerate(zip(example_paths, solution_paths)):
       base64_eg = encode_image(eg_path)
       base64_sol = encode_image(sol_path)
       image_contents.append({"role": "user", "content": [
          {"type": "text", "text": "Observe this input-output image pair"},
          {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{base64_eg}"}},
          {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{base64_sol}"}},
       ]})
       image_contents.append({"role": "assistant", "content": "Got it, ready to receive more examples"})
    
    messages = [{"role": "system", "content": SYSTEM_PROMPT}] + image_contents + [{"role": "user", "content": "Ok the above were all the examples, here's a human exaplanation for how to solve the problem and think about it, your objective is to create thinking steps and reasoning chains for it.\n\nEXPLANATION:\n"+explanation}]

    payload = {
        "model": "gpt-4.1",
        "messages": messages,
            "tools": [
                {
                    "type": "function",
                    "function": {
                        "name": "get_explanation",
                        "description": "Your goal is to produce an explanation so detailed and well-structured that it could serve as exemplary training data for teaching machines to reason through similar problems. While the human explanation is correct, your response should fill in all implicit reasoning steps and create a comprehensive record of the problem-solving process.",
                        "parameters": {
                            "type": "object",
                            "properties": {
                                "understanding_the_images": {
                                    "type": "string",
                                },
                                "solving": {
                                    "type": "string",
                                }
                            },
                            "required": [
                                "understanding_the_images",
                                "solving"
                            ],
                            "additionalProperties": False
                        },
                        "strict": True
                    }
                }
        ],
        "tool_choice": "required"
    }
    response_base = requests.post("https://api.openai.com/v1/chat/completions", headers=headers, json=payload)
    response_base = json.dumps(response_base.json()['choices'][0]['message']['tool_calls'][0]['function']['arguments'], indent=4)

    messages = [{"role": "system", "content": "Hey, you're a coding assistant. Read this description of a challenge and write a python code specifically a function called `convert` to input the input_matrix to an output matrix"}] + image_contents + [{"role": "user", "content": "Ok the above were all the examples, here's an exaplanation on how to solve the problem.\n\nEXPLANATION:\n"+response_base}]

    payload = {
        "model": "gpt-4o",
        "messages": messages,
            "tools": [
                {
                    "type": "function",
                    "function": {
                        "name": "get_code",
                        "description": "Straight runnable code, for a function which can be imported and executed, no other string, just begin with code. Use ```python and ``` as delimiters.",
                        "parameters": {
                            "type": "object",
                            "properties": {
                                "code": {
                                    "type": "string",
                                }
                            },
                            "required": [
                                "code"
                            ],
                            "additionalProperties": False
                        },
                        "strict": True
                    }
                }
        ],
        "tool_choice": "required"
    }
    response_code = requests.post("https://api.openai.com/v1/chat/completions", headers=headers, json=payload)
    response_code = json.dumps(response_code.json()['choices'][0]['message']['tool_calls'][0]['function']['arguments'], indent=4)
    return json.dumps([response_base, response_code], indent=4)
