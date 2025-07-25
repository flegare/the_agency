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
        model="llama2", # Or any other model you have available
        messages=[
            {
                'role': 'user',
                'content': prompt,
            },
        ],
    )
    
    try:
        # Attempt to parse the entire content as JSON
        suggestions = json.loads(response['message']['content'])
        return suggestions
    except json.JSONDecodeError:
        # If direct parsing fails, try to extract JSON by finding the first { and last }
        content = response['message']['content']
        start_index = content.find('{')
        end_index = content.rfind('}')
        
        if start_index != -1 and end_index != -1 and end_index > start_index:
            json_string = content[start_index : end_index + 1]
            try:
                suggestions = json.loads(json_string)
                return suggestions
            except json.JSONDecodeError as e:
                return { "error": "Failed to parse extracted JSON", "details": str(e), "response": response['message']['content'] }
        else:
            # Fallback if no valid JSON block is found
            return { "error": "No valid JSON output found in LLM response", "response": response['message']['content'] }
    except KeyError as e:
        return { "error": "Missing key in LLM response", "details": str(e), "response": response['message']['content'] }

@app.get("/")
def read_root():
    return {"message": "Name Generator Agent is running"}
