from fastapi import FastAPI
from pydantic import BaseModel
import ollama
import json
import re

app = FastAPI()

class ProjectBrief(BaseModel):
    project_brief: str
    objectives: list[str]
    criteria_of_success: list[str]
    high_level_features: list[str]

@app.post("/generate_solution_approach")
async def generate_solution_approach(brief: ProjectBrief):
    prompt = f"""
    You are a Solution Architect agent. Your task is to take a project brief and generate a detailed solution approach.
    The solution approach should include:
    1.  **Technical Approach:** Proposed technologies, architecture, and design patterns.
    2.  **High-Level Stories/Activities:** A list of well-documented high-level stories or activities that need to be done to make this project.
    3.  **Testing Strategy:** A high-level plan for how the solution will be tested.

    Project Brief:
    {brief.project_brief}

    Objectives:
    {brief.objectives}

    Criteria of Success:
    {brief.criteria_of_success}

    High-Level Features:
    {brief.high_level_features}

    Return the output as a valid JSON object with the following keys: "technical_approach", "high_level_stories", and "testing_strategy".
    The "high_level_stories" should be an array of strings.

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
        solution_data = json.loads(json_string)
        return solution_data
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
    return {"message": "Solution Architect Agent is running"}
