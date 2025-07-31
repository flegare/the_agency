import requests
import json
import time
import os

AGENT_URL = "http://localhost:8000/generate_name"
LOGS_DIR = "logs"

def test_agent_single_model(description: str, model_name: str):
    print(f"\n--- Testing with {model_name} ---")
    payload = {"description": description}
    start_time = time.time()
    
    result_output = []
    result_output.append(f"--- Test Results for {model_name} ---")

    try:
        response = requests.post(AGENT_URL, json=payload)
        response.raise_for_status()  # Raise an exception for HTTP errors
        data = response.json()
        end_time = time.time()
        time_taken = end_time - start_time
        result_output.append(f"Time taken: {time_taken:.2f} seconds")
        
        if "suggestions" in data:
            result_output.append("Generated Suggestions:")
            for i, suggestion in enumerate(data["suggestions"]):
                result_output.append(f"{i+1}. Name: {suggestion['name']}, Tagline: {suggestion['tagline']}")
            success = True
        else:
            result_output.append(f"Error: {data.get('error', 'Unknown error')}")
            result_output.append(f"Response: {data.get('response', 'No response content')}")
            success = False
            
    except requests.exceptions.RequestException as e:
        result_output.append(f"Request failed: {e}")
        success = False
        time_taken = time.time() - start_time # Record time even on failure

    # Save results to file
    os.makedirs(LOGS_DIR, exist_ok=True)
    file_path = os.path.join(LOGS_DIR, f"results_{model_name}.txt")
    with open(file_path, "w") as f:
        f.write("\n".join(result_output))
    print(f"Results saved to {file_path}")
    
    return success, data, time_taken

if __name__ == "__main__":
    # This script is now designed to be run for a single model at a time.
    # The model name will be passed as an argument or set manually here.
    # For the purpose of this interaction, I will guide the user to set the model
    # in main.py and then call this script.
    
    # This part will be executed by me, after you've manually set the model.
    # The model name will be dynamically set by me in the next steps.
    pass