# Feature Brief: Documentation Agent

## Product Owner Request

To enhance the project's maintainability and understanding, a new `Documentation Agent` is required. This agent will automate the generation of documentation from source code, initially focusing on Python files. The goal is to provide a foundational tool for creating up-to-date and consistent documentation.

## Solution Architect Plan

**Goal:** Develop a `Documentation Agent` that can extract information from Python source code and generate Markdown-formatted documentation.

1.  **Agent Structure:**
    *   Create a new directory: `documentation_agent/`.
    *   Inside `documentation_agent/`, create `main.py`, `requirements.txt`, and `Dockerfile`.

2.  **Core Functionality (`main.py`):**
    *   **FastAPI Application:** Set up a FastAPI application to expose API endpoints.
    *   **Endpoint: `/generate_docs` (POST):**
        *   **Request Body:** Accept a list of file paths (strings) to Python files.
        *   **Processing:** For each file:
            *   Read the file content.
            *   Use Python's `ast` module to parse the code and extract:
                *   Module-level docstrings.
                *   Class definitions (name, docstring, methods).
                *   Function definitions (name, docstring, parameters).
            *   Format the extracted information into Markdown.
        *   **Response:** Return a dictionary where keys are file paths and values are the generated Markdown strings.
    *   **Endpoint: `/health` (GET):** Standard health check endpoint.

3.  **Dependencies (`requirements.txt`):**
    *   `fastapi`
    *   `uvicorn`

4.  **Dockerization (`Dockerfile`):**
    *   Use a Python base image (e.g., `python:3.10-slim-buster`).
    *   Copy `requirements.txt` and install dependencies.
    *   Copy `main.py`.
    *   Expose port 8000.
    *   Define the `CMD` to run the FastAPI application with `uvicorn`.

## Testing Strategy

**Objective:** Verify that the `Documentation Agent` correctly extracts information from Python files and generates accurate Markdown documentation.

1.  **Unit Tests (`documentation_agent/test_main.py` - new file):**
    *   **Test Case 1: Module Docstring:**
        *   Create a dummy Python file with a module-level docstring.
        *   Call `/generate_docs` with this file.
        *   Assert that the generated Markdown contains the correct module docstring.
    *   **Test Case 2: Function Docstring and Parameters:**
        *   Create a dummy Python file with a function including a docstring and parameters.
        *   Call `/generate_docs` with this file.
        *   Assert that the generated Markdown correctly represents the function, its docstring, and parameters.
    *   **Test Case 3: Class Docstring and Methods:**
        *   Create a dummy Python file with a class including a docstring and methods.
        *   Call `/generate_docs` with this file.
        *   Assert that the generated Markdown correctly represents the class, its docstring, and methods.
    *   **Test Case 4: Empty File/No Docstrings:**
        *   Create a dummy Python file with no docstrings or definitions.
        *   Call `/generate_docs` with this file.
        *   Assert that the generated Markdown is empty or contains only basic file information.
    *   **Test Case 5: Multiple Files:**
        *   Create multiple dummy Python files.
        *   Call `/generate_docs` with all files.
        *   Assert that the response contains documentation for all files.
    *   **Test Case 6: File Not Found:**
        *   Call `/generate_docs` with a non-existent file path.
        *   Assert that the agent returns an appropriate error (e.g., 404 or a specific error message).

2.  **Integration Tests (Manual/Scripted):**
    *   **Setup:** Ensure the `Documentation Agent` is running in its Docker container.
    *   **Verification:** Use `curl` commands to call the `/generate_docs` endpoint with various real Python files from the project (e.g., `root_agent/main.py`, `historian_agent/main.py`). Manually inspect the generated Markdown for correctness and completeness.
