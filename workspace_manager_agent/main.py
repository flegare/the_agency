# /home/cortex/agents_tools/workspace_manager_agent/main.py
import os
import shutil
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

@app.post("/stop_project", summary="Stop a project by killing its process or stopping its container")
def stop_project(request: ProjectRequest):
    project_path = os.path.join(WORKSPACE_DIR, request.project_name)
    stop_script = os.path.join(project_path, "stop.sh")
    pid_file = os.path.join(project_path, ".pid")

    if not os.path.exists(project_path):
        return {"status": f"Project {request.project_name} not found, nothing to stop."}

    # Priority 1: Use stop.sh if it exists (most specific, good for docker-compose)
    if os.path.exists(stop_script):
        print(f"Using stop.sh for project {request.project_name}")
        subprocess.run(["bash", stop_script], cwd=project_path, capture_output=True, text=True)
        return {"status": f"Executed stop.sh for {request.project_name}"}

    # Priority 2: Use .pid file if it exists (for simple processes or single containers)
    elif os.path.exists(pid_file):
        print(f"Using .pid file for project {request.project_name}")
        with open(pid_file, 'r') as f:
            pid_or_name = f.read().strip()
        
        # Try to kill as a PID first
        try:
            pid = int(pid_or_name)
            os.kill(pid, 15)  # 15 = SIGTERM
            os.remove(pid_file)
            return {"status": f"Kill command issued for process {pid} of project {request.project_name}"}
        except ValueError:
            # It's a container name
            container_name = pid_or_name
            print(f"Attempting to stop Docker container by name: {container_name}")
            subprocess.run(["docker", "stop", container_name], capture_output=True, text=True)
            subprocess.run(["docker", "rm", container_name], capture_output=True, text=True)
            os.remove(pid_file)
            return {"status": f"Docker container {container_name} stopped and removed."}
        except ProcessLookupError:
            print(f"Process with PID {pid_or_name} not found. Removing stale .pid file.")
            os.remove(pid_file) # Clean up stale file
            return {"status": f"Stale process {pid_or_name} for project {request.project_name} cleaned up."}
    
    else:
        # No stop method found
        raise HTTPException(status_code=404, detail=f"No stop method (stop.sh or .pid) found for project {request.project_name}")

@app.get("/get_logs", summary="Get the logs for a project")
def get_logs(project_name: str):
    project_path = os.path.join(WORKSPACE_DIR, project_name)
    log_file = os.path.join(project_path, "project.log")
    if not os.path.exists(log_file):
        raise HTTPException(status_code=404, detail="project.log not found")
    with open(log_file, 'r') as f:
        return {"logs": f.read()}

@app.post("/delete_project", summary="Delete a project and all its files")
def delete_project(request: ProjectRequest):
    project_path = os.path.join(WORKSPACE_DIR, request.project_name)
    if not os.path.exists(project_path):
        raise HTTPException(status_code=404, detail="Project not found")

    # First, try to stop the project if it's running
    try:
        stop_project(request)
    except HTTPException as e:
        # Ignore errors if the project wasn't running (e.g., no stop.sh or .pid file)
        print(f"Note: Could not stop project {request.project_name} (may have already been stopped): {e.detail}")

    # Now, delete the directory
    shutil.rmtree(project_path)
    return {"status": f"Project {request.project_name} has been deleted"}

@app.get("/health", summary="Health check endpoint")
def health_check() -> dict:
    """Returns a success message to indicate that the agent is running."""
    return {"status": "ok"}
