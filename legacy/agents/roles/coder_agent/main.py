from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from curl_wrapper import run_curl_command
import json
import re
import tempfile
import os

app = FastAPI()

# Define a temporary directory within the agent's own directory
AGENT_TMP_DIR = os.path.join(os.path.dirname(__file__), "tmp")
os.makedirs(AGENT_TMP_DIR, exist_ok=True)

class CodeGenerationRequest(BaseModel):
    high_level_stories: list[str]
    context: str | None = None
    task_description: str

@app.post("/generate_code")
async def generate_code(request: CodeGenerationRequest):
    prompt = f"""
    You are a Coder agent. Your task is to generate code based on the provided high-level stories, context, and a specific task description.
    
    High-Level Stories:
    {request.high_level_stories}

    Context:
    {request.context if request.context else "No additional context provided."}

    Task Description:
    {request.task_description}

    Generate the code. Provide the code within a markdown code block, and explain your reasoning briefly before the code block.
    """

    # Construct the JSON payload for the Ollama chat API
    payload = {
        "model": "deepseek-r1",
        "messages": [
            {
                "role": "user",
                "content": prompt,
            }
        ]
    }
    
    # Convert payload to a JSON string
    json_payload = json.dumps(payload)

    # Define the curl command arguments
    curl_args = [
        "-X", "POST",
        "http://localhost:11434/api/chat",
        "-H", "Content-Type: application/json",
        "-d", json_payload
    ]

    # Run the curl command using the wrapper
    curl_result = run_curl_command(curl_args)

    if curl_result["status"] == "error":
        raise HTTPException(status_code=500, detail=f"Ollama API call failed: {curl_result['message']}")

    # Parse the JSON response from curl, handling streamed output
    full_content = ""
    try:
        for line in curl_result["output"].splitlines():
            if line.strip():  # Ensure the line is not empty
                json_response = json.loads(line)
                if "message" in json_response and "content" in json_response["message"]:
                    full_content += json_response["message"]["content"]
                if json_response.get("done"): # Check for the 'done' flag
                    break
        content = full_content
    except json.JSONDecodeError as e:
        raise HTTPException(status_code=500, detail=f"Failed to parse Ollama API response as JSON: {e.msg}")
    except KeyError as e:
        raise HTTPException(status_code=500, detail=f"Unexpected Ollama API response format: Missing key {e}")

    # Write the content to a temporary file within the agent's tmp directory
    fd, absolute_path = tempfile.mkstemp(suffix=".txt", prefix="coder_agent_output_", dir=AGENT_TMP_DIR)
    with os.fdopen(fd, 'w') as tmp:
        tmp.write(content)

    # Return the absolute path for the Gemini CLI to read
    return {"output_file": absolute_path}

@app.get("/health", summary="Health check endpoint")
def health_check() -> dict:
    """Returns a success message to indicate that the agent is running."""
    return {"status": "ok"}

@app.get("/")
async def read_root():
    return {"message": "Coder Agent is running"}
