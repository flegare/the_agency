# Project Knowledge Base

This document summarizes the current state and key technologies used in the Gemini CLI agent project.

## Project Goal
The overarching goal of this project is to create a collection of specialized, independent agents that extend the Gemini CLI's capabilities, mimicking a virtual IT department.

## Current Agents and Their Purpose

### 1. Name Generator Agent
- **Location:** `name_generator_agent/`
- **Purpose:** Generates creative project name suggestions and taglines based on a given project description.
- **Dockerized:** Yes.
- **Key Technologies:**
    - FastAPI: For building the agent's API.
    - Uvicorn: ASGI server to run the FastAPI application.
    - Ollama: Used for interacting with local large language models (LLMs) to generate names.
    - `deepseek-r1` model: The currently configured LLM for name generation.
- **Dependencies:** `fastapi`, `uvicorn`, `langchain-community`, `ollama`

### 2. Ollama Agent
- **Location:** `ollama_agent/`
- **Purpose:** Provides an interface for interacting with Ollama, likely to manage models or run inferences.
- **Dockerized:** Yes.
- **Key Technologies:**
    - FastAPI: For building the agent's API.
    - Uvicorn: ASGI server.
    - httpx: For making HTTP requests (e.g., to the Ollama server).
- **Dependencies:** `fastapi`, `uvicorn`, `httpx`

### 3. Web Surfer Agent
- **Location:** `web_surfer_agent/`
- **Purpose:** Enables web browsing capabilities, such as taking screenshots and clicking elements on web pages.
- **Dockerized:** Yes.
- **Key Technologies:** (Details to be added as implemented, but likely involves a headless browser like Playwright/Selenium)
- **Dependencies:** (To be determined)

### 4. File Analyzer Agent
- **Location:** `file_analyzer_agent/`
- **Purpose:** Analyzes files, likely for content, structure, or type.
- **Dockerized:** Yes.
- **Key Technologies:** (Details to be added as implemented)
- **Dependencies:** (To be determined)

### 5. Secret Manager Agent
- **Location:** `secret_manager_agent/`
- **Purpose:** Manages secrets and sensitive information.
- **Dockerized:** Yes.
- **Key Technologies:** (Details to be added as implemented)
- **Dependencies:** (To be determined)

### 6. Workspace Manager Agent
- **Location:** `workspace_manager_agent/`
- **Purpose:** Manages project workspaces, including creation and removal of project environments. Now supports creating Docker-based projects from templates for true environment isolation.
- **Dockerized:** Yes.
- **Key Technologies:** (Details to be added as implemented)
- **Dependencies:** (To be determined)

## Development Workflow
The project follows a Virtual IT Team workflow:
- **Product Owner:** User (provides requests).
- **Solution Architect (Me):** Creates Feature Briefs, defines technical approach, and testing strategy.
- **Coder (Me):** Implements features.
- **Tester (Me):** Develops and executes test plans.

## General Technical Stack
- **Language:** Python
- **Frameworks:** FastAPI for agents, Uvicorn for serving.
- **Environment Management:** Python virtual environments (`.venv`).
- **Version Control:** Git.
- **LLM Interaction:** Ollama for local model inference.

### 7. Historian Agent
- **Location:** `historian_agent/`
- **Purpose:** Tracks project evolution, actions, and key learnings, and archives useful files for seamless session resumption.
- **Dockerized:** Yes.
- **Key Technologies:**
    - FastAPI: For building the agent's API.
    - Uvicorn: ASGI server.
    - datetime, json, shutil: For managing archives.
- **Dependencies:** `fastapi`, `uvicorn`

### 8. Coder Agent
- **Location:** `coder_agent/`
- **Purpose:** Generates code based on high-level stories, context, and task descriptions using an LLM.
- **Dockerized:** Yes.
- **Key Technologies:**
    - FastAPI: For building the agent's API.
    - Uvicorn: ASGI server.
    - Ollama: Used for interacting with local large language models (LLMs) to generate code.
    - `deepseek-r1` model: The currently configured LLM for code generation.
    - curl_wrapper: Custom wrapper for making curl requests.
- **Dependencies:** `fastapi`, `uvicorn`

### 9. Solution Architect Agent
- **Location:** `solution_architect_agent/`
- **Purpose:** Generates detailed solution approaches (technical approach, high-level stories, testing strategy) from a project brief using an LLM.
- **Dockerized:** Yes.
- **Key Technologies:**
    - FastAPI: For building the agent's API.
    - Uvicorn: ASGI server.
    - Ollama: Used for interacting with local large language models (LLMs).
    - `deepseek-r1` model: The currently configured LLM.
- **Dependencies:** `fastapi`, `uvicorn`

### 10. Tester Agent
- **Location:** `tester_agent/`
- **Purpose:** Generates detailed test plans (objectives, scope, strategy, cases, environment, tools) from a solution approach using an LLM.
- **Dockerized:** Yes.
- **Key Technologies:**
    - FastAPI: For building the agent's API.
    - Uvicorn: ASGI server.
    - Ollama: Used for interacting with local large language models (LLMs).
    - `deepseek-r1` model: The currently configured LLM.
- **Dependencies:** `fastapi`, `uvicorn`

### 11. Root Agent
- **Location:** `root_agent/`
- **Purpose:** Orchestrates other agents, providing a unified interface for managing and interacting with the entire suite of agents.
- **Dockerized:** Yes.
- **Key Technologies:**
    - FastAPI: For building the agent's API.
    - Uvicorn: ASGI server.
    - Subprocess: For calling other agents via curl.
- **Dependencies:** `fastapi`, `uvicorn`

## Future Considerations
- **Docker for Isolation:** Implemented. Project creation now uses Docker for true environment isolation.
- **Root Agent:** Implemented. Orchestrates other agents.
