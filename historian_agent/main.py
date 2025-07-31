from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import os
import datetime
import json
import shutil

app = FastAPI()

HISTORY_DIR = "history"
os.makedirs(HISTORY_DIR, exist_ok=True)

class ArchiveSessionRequest(BaseModel):
    session_summary: str
    files_to_archive: list[str] = []

class LoadContextRequest(BaseModel):
    timestamp: str | None = None # Optional: if user wants a specific session

@app.post("/archive_session")
async def archive_session(request: ArchiveSessionRequest):
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    session_archive_dir = os.path.join(HISTORY_DIR, timestamp)
    os.makedirs(session_archive_dir, exist_ok=True)

    # Save session summary
    summary_path = os.path.join(session_archive_dir, "session_summary.md")
    with open(summary_path, "w") as f:
        f.write(request.session_summary)

    # Archive specified files
    archived_files = []
    for file_path in request.files_to_archive:
        if os.path.exists(file_path):
            try:
                shutil.copy(file_path, session_archive_dir)
                archived_files.append(os.path.basename(file_path))
            except Exception as e:
                print(f"Error archiving file {file_path}: {e}")
        else:
            print(f"File not found for archiving: {file_path}")

    return {"status": "success", "message": f"Session archived to {timestamp}", "archived_files": archived_files}

@app.post("/load_context")
async def load_context(request: LoadContextRequest):
    if request.timestamp:
        target_dir = os.path.join(HISTORY_DIR, request.timestamp)
        if not os.path.isdir(target_dir):
            raise HTTPException(status_code=404, detail="Session archive not found.")
    else:
        # Get the latest session if no timestamp is provided
        all_sessions = sorted(os.listdir(HISTORY_DIR), reverse=True)
        if not all_sessions:
            raise HTTPException(status_code=404, detail="No session archives found.")
        target_dir = os.path.join(HISTORY_DIR, all_sessions[0])

    summary_path = os.path.join(target_dir, "session_summary.md")
    if not os.path.exists(summary_path):
        raise HTTPException(status_code=404, detail="Session summary not found in archive.")

    with open(summary_path, "r") as f:
        session_summary = f.read()

    archived_files_list = os.listdir(target_dir)
    # Filter out the summary file itself
    archived_files_list = [f for f in archived_files_list if f != "session_summary.md"]

    return {"status": "success", "session_summary": session_summary, "archived_files": archived_files_list}

@app.get("/health", summary="Health check endpoint")
def health_check() -> dict:
    """Returns a success message to indicate that the agent is running."""
    return {"status": "ok"}

@app.get("/")
async def read_root():
    return {"message": "Historian Agent is running"}
