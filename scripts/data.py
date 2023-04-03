import os

def load_prompt():
    try:
        # Get the current script's directory
        script_dir = os.path.dirname(os.path.realpath(__file__))
        
        # Construct the absolute path to the prompt.txt file
        prompt_file_path = os.path.join(script_dir, "data", "prompt.txt")

        # Load the prompt from data/prompt.txt
        with open(prompt_file_path, "r") as prompt_file:
            prompt = prompt_file.read()

        return prompt
    except FileNotFoundError:
        print("Error: Prompt file not found", flush=True)
        return ""
