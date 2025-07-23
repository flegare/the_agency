# /home/cortex/agents_tools/workspace_manager_agent/main.py
import os
import subprocess
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

app = FastAPI(
    title="Workspace Manager Agent",
    description="An agent that can create, start, stop, and monitor projects.",
    version="1.0.0",
)

WORKSPACE_DIR = "/home/cortex/agents_tools/workspace"

class ProjectRequest(BaseModel):
    project_name: str

@app.post("/create_project", summary="Create a new project directory")
def create_project(request: ProjectRequest):
    project_path = os.path.join(WORKSPACE_DIR, request.project_name)
    if os.path.exists(project_path):
        raise HTTPException(status_code=400, detail="Project already exists")
    os.makedirs(project_path)
    return {"status": "success", "path": project_path}

@app.post("/start_project", summary="Start a project by executing its start.sh script")
def start_project(request: ProjectRequest):
    project_path = os.path.join(WORKSPACE_DIR, request.project_name)
    start_script = os.path.join(project_path, "start.sh")
    if not os.path.exists(start_script):
        raise HTTPException(status_code=404, detail="start.sh not found")
    
    # Execute start.sh in the background
    subprocess.Popen(["bash", start_script], cwd=project_path)
    return {"status": f"Start command issued for {request.project_name}"}

@app.post("/stop_project", summary="Stop a project by killing its process")
def stop_project(request: ProjectRequest):
    project_path = os.path.join(WORKSPACE_DIR, request.project_name)
    pid_file = os.path.join(project_path, ".pid")
    if not os.path.exists(pid_file):
        raise HTTPException(status_code=404, detail=".pid file not found")
    with open(pid_file, 'r') as f:
        pid = int(f.read().strip())
    try:
        os.kill(pid, 15) # 15 = SIGTERM
        os.remove(pid_file)
    except ProcessLookupError:
        raise HTTPException(status_code=404, detail=f"Process with PID {pid} not found.")
    return {"status": f"Stop command issued for {request.project_name}"}

@app.get("/get_logs", summary="Get the logs for a project")
def get_logs(project_name: str):
    project_path = os.path.join(WORKSPACE_DIR, project_name)
    log_file = os.path.join(project_path, "project.log")
    if not os.path.exists(log_file):
        raise HTTPException(status_code=404, detail="project.log not found")
    with open(log_file, 'r') as f:
        return {"logs": f.read()}

@app.get("/health", summary="Health check endpoint")
def health_check() -> dict:
    """Returns a success message to indicate that the agent is running."""
    return {"status": "ok"}
