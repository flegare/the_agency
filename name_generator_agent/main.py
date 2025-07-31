from fastapi import FastAPI
from pydantic import BaseModel
import ollama
import json
import re

app = FastAPI()

class ProjectDescription(BaseModel):
    description: str

@app.post("/generate_name")
def generate_name(project: ProjectDescription):
    """
    Generates project name suggestions based on a description.
    """
    prompt = f"""
    You are an expert in branding and naming projects.
    Given the following project description, generate 5 creative and suitable names.
    For each name, provide a short, compelling tagline.
    Return the output as a valid JSON object with a single key "suggestions" which is an array of objects, where each object has "name" and "tagline" keys.

    Project Description:
    {project.description}

    JSON Output:
    """

    response = ollama.chat(
        model="deepseek-r1", # Or any other model you have available
        messages=[
            {
                'role': 'user',
                'content': prompt,
            },
        ],
    )
    
    content = response['message']['content']

    # First, try to extract JSON from a markdown code block
    json_match = re.search(r'```json\n(.*)\n```', content, re.DOTALL)
    if json_match:
        json_string = json_match.group(1)
    else:
        # Fallback: try to extract JSON by finding the first { and last }
        start_index = content.find('{')
        end_index = content.rfind('}')
        
        if start_index != -1 and end_index != -1 and end_index > start_index:
            json_string = content[start_index : end_index + 1]
        else:
            return { "error": "No valid JSON output found in LLM response", "response": content }

    try:
        suggestions = json.loads(json_string)
        return suggestions
    except json.JSONDecodeError as e:
        return { "error": "Failed to parse extracted JSON", "details": str(e), "response": content }
    except KeyError as e:
        return { "error": "Missing key in LLM response", "details": str(e), "response": content }

@app.get("/health", summary="Health check endpoint")
def health_check() -> dict:
    """Returns a success message to indicate that the agent is running."""
    return {"status": "ok"}

@app.get("/")
def read_root():
    return {"message": "Name Generator Agent is running"}