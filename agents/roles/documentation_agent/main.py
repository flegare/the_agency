from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import os
import ast

app = FastAPI(
    title="Documentation Agent",
    description="An agent that generates documentation from source code.",
    version="1.0.0",
)

class GenerateDocsRequest(BaseModel):
    file_paths: list[str]

def generate_markdown_from_python_file(file_path: str) -> str:
    markdown_output = f"# Documentation for {os.path.basename(file_path)}\n\n"
    try:
        with open(file_path, "r") as f:
            tree = ast.parse(f.read())

        # Module-level docstring
        if ast.get_docstring(tree):
            markdown_output += f"## Overview\n\n{ast.get_docstring(tree)}\n\n"

        for node in tree.body:
            if isinstance(node, ast.ClassDef):
                markdown_output += f"## Class: `{node.name}`\n\n"
                if ast.get_docstring(node):
                    markdown_output += f"{ast.get_docstring(node)}\n\n"
                for item in node.body:
                    if isinstance(item, ast.FunctionDef):
                        markdown_output += f"### Method: `{item.name}`\n\n"
                        if ast.get_docstring(item):
                            markdown_output += f"{ast.get_docstring(item)}\n\n"
                        if item.args.args:
                            params = ", ".join([arg.arg for arg in item.args.args])
                            markdown_output += f"**Parameters:** `{params}`\n\n"
            elif isinstance(node, ast.FunctionDef):
                markdown_output += f"## Function: `{node.name}`\n\n"
                if ast.get_docstring(node):
                    markdown_output += f"{ast.get_docstring(node)}\n\n"
                if node.args.args:
                    params = ", ".join([arg.arg for arg in node.args.args])
                    markdown_output += f"**Parameters:** `{params}`\n\n"

    except FileNotFoundError:
        raise HTTPException(status_code=404, detail=f"File not found: {file_path}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing file {file_path}: {str(e)}")

    return markdown_output

@app.post("/generate_docs", summary="Generate Markdown documentation from Python files")
async def generate_docs(request: GenerateDocsRequest):
    all_docs = {}
    for file_path in request.file_paths:
        # Ensure the path is absolute and within a safe directory if needed in a real scenario
        # For this example, we'll assume paths are relative to the project root or absolute and accessible
        try:
            docs = generate_markdown_from_python_file(file_path)
            all_docs[file_path] = docs
        except HTTPException as e:
            all_docs[file_path] = f"Error: {e.detail}"
        except Exception as e:
            all_docs[file_path] = f"Error: An unexpected error occurred: {str(e)}"

    return {"status": "success", "documentation": all_docs}

@app.get("/health", summary="Health check endpoint")
def health_check() -> dict:
    """Returns a success message to indicate that the agent is running."""
    return {"status": "ok"}
