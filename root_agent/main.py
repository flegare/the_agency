from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import os
import json
import httpx # Import httpx

app = FastAPI(
    title="Root Agent",
    description="An agent that orchestrates other agents.",
    version="1.0.0",
)

AGENT_PORTS_FILE = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), ".agent_ports")

class AgentCallRequest(BaseModel):
    agent_name: str
    endpoint: str
    method: str = "POST"
    payload: dict | None = None

@app.get("/list_agents", summary="List all running agents")
async def list_agents():
    agents_info = []
    if os.path.exists(AGENT_PORTS_FILE):
        with open(AGENT_PORTS_FILE, 'r') as f:
            for line in f:
                parts = line.strip().split(':')
                if len(parts) == 2:
                    agent_name, port = parts
                    agents_info.append({"name": agent_name, "port": int(port)})
    return {"agents": agents_info}

@app.post("/call_agent", summary="Call an endpoint on a specific agent")
async def call_agent(request: AgentCallRequest):
    agents_list = await list_agents()
    target_agent = None
    for agent in agents_list["agents"]:
        if agent["name"] == request.agent_name:
            target_agent = agent
            break

    if not target_agent:
        raise HTTPException(status_code=404, detail=f"Agent {request.agent_name} not found or not running.")

    # Use environment variables for inter-agent communication
    # The format is AGENT_NAME_HOST=container_name
    agent_host = os.getenv(f"{request.agent_name.upper().replace('-', '_')}_HOST", "localhost")
    url = f"http://{agent_host}:8000/{request.endpoint}" # Agents listen on 8000 internally
    
    async with httpx.AsyncClient() as client:
        try:
            if request.method.upper() == "POST":
                response = await client.post(url, json=request.payload)
            elif request.method.upper() == "GET":
                response = await client.get(url, params=request.payload)
            # Add other methods (PUT, DELETE, etc.) as needed
            else:
                raise HTTPException(status_code=400, detail=f"Unsupported HTTP method: {request.method}")
            
            response.raise_for_status() # Raise an exception for 4xx/5xx responses
            return {"status": "success", "response": response.json()}
        except httpx.RequestError as e:
            raise HTTPException(status_code=500, detail=f"Agent call failed due to network error: {e}")
        except httpx.HTTPStatusError as e:
            raise HTTPException(status_code=e.response.status_code, detail=f"Agent call failed with HTTP error: {e.response.text}")
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"An unexpected error occurred: {str(e)}")

@app.get("/health", summary="Health check endpoint")
def health_check() -> dict:
    """Returns a success message to indicate that the agent is running."""
    return {"status": "ok"}
