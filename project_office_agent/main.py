from fastapi import FastAPI
from pydantic import BaseModel
import ollama
import json
import re

app = FastAPI()

class ProjectAbstract(BaseModel):
    abstract: str

@app.post("/generate_project_brief")
async def generate_project_brief(project: ProjectAbstract):
    prompt = f"""
    You are a Project Office agent. Your task is to take an abstract project description and generate a detailed project brief.
    The project brief should include:
    1.  **Project Brief:** A concise summary of the project.
    2.  **Objectives:** Clear, measurable objectives for the project.
    3.  **Criteria of Success:** How the success of the project will be measured.
    4.  **High-Level Features (To-Do List):** A list of high-level features or tasks that need to be done to achieve the project objectives.

    Return the output as a valid JSON object with the following keys: "project_brief", "objectives", "criteria_of_success", and "high_level_features".
    The "high_level_features" should be an array of strings.

    Project Abstract:
    {project.abstract}

    JSON Output:
    """

    response = ollama.chat(
        model="deepseek-r1",
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
        brief_data = json.loads(json_string)
        return brief_data
    except json.JSONDecodeError as e:
        return { "error": "Failed to parse extracted JSON", "details": str(e), "response": content }
    except KeyError as e:
        return { "error": "Missing key in LLM response", "details": str(e), "response": content }

@app.get("/health", summary="Health check endpoint")
def health_check() -> dict:
    """Returns a success message to indicate that the agent is running."""
    return {"status": "ok"}

@app.get("/")
async def read_root():
    return {"message": "Project Office Agent is running"}