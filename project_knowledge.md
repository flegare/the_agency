# Project Knowledge Base

This document summarizes the current state and key technologies used in the Gemini CLI agent project.

## Project Goal
The overarching goal of this project is to create a collection of specialized, independent agents that extend the Gemini CLI's capabilities, mimicking a virtual IT department.

## Current Agents and Their Purpose

### 1. Name Generator Agent
- **Location:** `name_generator_agent/`
- **Purpose:** Generates creative project name suggestions and taglines based on a given project description.
- **Key Technologies:**
    - FastAPI: For building the agent's API.
    - Uvicorn: ASGI server to run the FastAPI application.
    - Ollama: Used for interacting with local large language models (LLMs) to generate names.
    - `deepseek-r1` model: The currently configured LLM for name generation.
- **Dependencies:** `fastapi`, `uvicorn`, `langchain-community`, `ollama`

### 2. Ollama Agent (Planned/Underlying)
- **Location:** `ollama_agent/`
- **Purpose:** (Implicit) Provides an interface for interacting with Ollama, likely to manage models or run inferences.
- **Key Technologies:**
    - FastAPI: For building the agent's API.
    - Uvicorn: ASGI server.
    - httpx: For making HTTP requests (e.g., to the Ollama server).
- **Dependencies:** `fastapi`, `uvicorn`, `httpx`

### 3. Web Surfer Agent
- **Location:** `web_surfer_agent/`
- **Purpose:** Enables web browsing capabilities, such as taking screenshots and clicking elements on web pages.
- **Key Technologies:** (Details to be added as implemented, but likely involves a headless browser like Playwright/Selenium)
- **Dependencies:** (To be determined)

### 4. File Analyzer Agent
- **Location:** `file_analyzer_agent/`
- **Purpose:** Analyzes files, likely for content, structure, or type.
- **Key Technologies:** (Details to be added as implemented)
- **Dependencies:** (To be determined)

### 5. Secret Manager Agent
- **Location:** `secret_manager_agent/`
- **Purpose:** Manages secrets and sensitive information.
- **Key Technologies:** (Details to be added as implemented)
- **Dependencies:** (To be determined)

### 6. Workspace Manager Agent
- **Location:** `workspace_manager_agent/`
- **Purpose:** Manages project workspaces, including creation and removal of project environments (e.g., Firebase projects).
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

## Future Considerations
- **Docker for Isolation:** High priority to re-architect project creation to use Docker for true environment isolation.
- **Root Agent:** Future plan to create a "root agent" to orchestrate other agents.
