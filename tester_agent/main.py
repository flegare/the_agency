from fastapi import FastAPI
from pydantic import BaseModel
import ollama
import json
import re

app = FastAPI()

class SolutionApproach(BaseModel):
    technical_approach: dict
    high_level_stories: list[str]
    testing_strategy: dict

@app.post("/generate_test_plan")
async def generate_test_plan(solution: SolutionApproach):
    prompt = f"""
    You are a Tester agent. Your task is to take a solution approach and generate a detailed test plan.
    The test plan should include:
    1.  **Test Objectives:** What needs to be tested and why.
    2.  **Test Scope:** What will be included and excluded from testing.
    3.  **Test Strategy:** Types of testing to be performed (e.g., unit, integration, end-to-end, performance, security).
    4.  **Test Cases:** High-level test cases for each high-level story/activity.
    5.  **Test Environment:** Requirements for the testing environment.
    6.  **Tools:** Recommended testing tools.

    Solution Approach:
    Technical Approach: {solution.technical_approach}
    High-Level Stories: {solution.high_level_stories}
    Testing Strategy: {solution.testing_strategy}

    Return the output as a valid JSON object with the following keys: "test_objectives", "test_scope", "test_strategy", "test_cases", "test_environment", and "tools".
    The "test_cases" should be an array of strings, where each string represents a test case.

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
        test_plan_data = json.loads(json_string)
        return test_plan_data
    except json.JSONDecodeError as e:
        return { "error": "Failed to parse extracted JSON", "details": str(e), "response": content }
    except KeyError as e:
        return { "error": "Missing key in LLM response", "details": str(e), "response": content }

@app.get("/")
async def read_root():
    return {"message": "Tester Agent is running"}
