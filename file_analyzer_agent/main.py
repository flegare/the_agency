# /home/cortex/agents_tools/file_analyzer_agent/main.py
from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI(
    title="File Analyzer Agent",
    description="An agent that can perform basic analysis on files.",
    version="1.0.0",
)

class FilePathRequest(BaseModel):
    path: str

@app.post("/count-lines", summary="Count lines in a file")
def count_lines(request: FilePathRequest) -> dict:
    """Takes a file path and returns the number of lines in it."""
    try:
        with open(request.path, 'r') as f:
            lines = sum(1 for line in f)
        return {"path": request.path, "line_count": lines}
    except Exception as e:
        return {"error": str(e)}
