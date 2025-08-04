# Agent Directory Structure

This document details the new organizational structure for agents within this project. The goal of this refactoring is to improve clarity, maintainability, and scalability by categorizing agents based on their primary function or role.

## New Structure

All agent directories are now located under the `agents/` directory at the project root. The structure follows the pattern:

`agents/<theme>/<agent_name>/`

Where:
*   **`agents/`**: The top-level directory for all agent implementations.
*   **`<theme>`**: A category that groups agents by their primary purpose or domain.
*   **`<agent_name>`**: The specific directory for an individual agent, containing its `Dockerfile`, `main.py`, `requirements.txt`, and any other related files.

## Themes and Their Purpose

### `core`

Agents in this theme are fundamental to the overall operation and orchestration of the Gemini CLI agent suite. They often provide foundational services or act as central coordination points.

*   **`root_agent`**: Orchestrates calls to other agents and provides a unified interface.

### `tools`

This theme includes agents that offer specific, often atomic, utility functions or interact with external services to perform a single, well-defined task. They are typically used by other agents or directly by the CLI for focused operations.

*   **`file_analyzer_agent`**: For analyzing file content.
*   **`google_drive_agent`**: For interacting with Google Drive.
*   **`name_generator_agent`**: For generating names.
*   **`ollama_agent`**: For interfacing with local Ollama instances.
*   **`secret_manager_agent`**: For managing secrets.
*   **`secure_executor_agent`**: For securely executing commands with injected secrets.
*   **`web_surfer_agent`**: For web browsing and interaction.

### `roles`

Agents in this theme embody a specific role or persona within a software development or project management lifecycle. They often combine functionalities from `tools` agents to perform more complex, high-level tasks associated with their designated role.

*   **`coder_agent`**: Focuses on code generation and modification.
*   **`documentation_agent`**: Handles documentation creation and management.
*   **`frontend_developer_agent`**: Specializes in frontend development tasks.
*   **`historian_agent`**: Manages project history and session context.
*   **`project_office_agent`**: Assists with project management and administrative tasks.
*   **`project_shipper_agent`**: Manages project deployment and release processes.
*   **`solution_architect_agent`**: Focuses on designing and planning technical solutions.
*   **`tester_agent`**: Handles testing and quality assurance.
*   **`workspace_manager_agent`**: Manages project workspaces and environments.

## Benefits of the New Structure

*   **Improved Discoverability**: Agents are easier to find and understand based on their category.
*   **Enhanced Maintainability**: Related agents are grouped together, simplifying navigation and updates.
*   **Scalability**: The structure can easily accommodate new agents and themes as the project grows.
*   **Clearer Responsibilities**: Each agent's purpose is more evident from its location.

This new structure aims to make the project more intuitive and efficient for both developers and users.
