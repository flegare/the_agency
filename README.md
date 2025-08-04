# Gemini Agents

This repository contains a collection of agents that can be used as tools by the Gemini CLI.

## Overview

The goal of this project is to create a suite of specialized agents that extend the capabilities of the Gemini CLI. Each agent is a small, independent web service that exposes its functionality through an OpenAPI specification. The Gemini CLI can discover and use these agents as tools.

## Agent Directory Structure

To improve organization and maintainability, agents are now categorized and located within a new `agents/` directory at the project root. The structure follows `agents/<theme>/<agent_name>`, where themes group agents by their primary function or role.

The current themes are:

*   **`core`**: Agents fundamental to the CLI's operation or orchestration.
*   **`tools`**: Agents that provide specific, often atomic, utility functions.
*   **`roles`**: Agents that embody a specific role or function within a software development lifecycle.

## Agents

Here's a categorized list of the agents in this repository:

### Core Agents
*   **Root Agent:** An agent that orchestrates other agents, providing a unified interface for managing and interacting with the entire suite of agents. (Located in `agents/core/root_agent`)

### Tool Agents
*   **File Analyzer Agent:** A simple agent that can perform basic analysis on files, such as counting lines. (Located in `agents/tools/file_analyzer_agent`)
*   **Google Drive Agent:** An agent for interacting with Google Drive services. (Located in `agents/tools/google_drive_agent`)
*   **Name Generator Agent:** An agent that can generate names. (Located in `agents/tools/name_generator_agent`)
*   **Ollama Agent:** An agent that can interface with a local Ollama instance. ([Documentation](docs/agents/tools/ollama_agent.md)) (Located in `agents/tools/ollama_agent`)
*   **Secret Manager Agent:** Manages secrets and sensitive information. (Located in `agents/tools/secret_manager_agent`)
*   **Secure Executor Agent:** Acts as an intermediary to securely inject secret values into commands before execution. (Located in `agents/tools/secure_executor_agent`)
*   **Web Surfer Agent:** An agent that can interact with web pages, take screenshots, and perform clicks. (Located in `agents/tools/web_surfer_agent`)

### Role Agents
*   **Coder Agent:** An agent focused on writing and modifying code. (Located in `agents/roles/coder_agent`)
*   **Documentation Agent:** An agent for generating and managing documentation. (Located in `agents/roles/documentation_agent`)
*   **Frontend Developer Agent:** An agent specialized in frontend development tasks. (Located in `agents/roles/frontend_developer_agent`)
*   **Historian Agent:** An agent that tracks project evolution, actions, and key learnings, and archives useful files for seamless session resumption. (Located in `agents/roles/historian_agent`)
*   **Project Office Agent:** An agent for project management and coordination tasks. (Located in `agents/roles/project_office_agent`)
*   **Project Shipper Agent:** An agent responsible for preparing and shipping projects. (Located in `agents/roles/project_shipper_agent`)
*   **Solution Architect Agent:** An agent for designing and planning technical solutions. (Located in `agents/roles/solution_architect_agent`)
*   **Tester Agent:** An agent focused on testing and quality assurance. (Located in `agents/roles/tester_agent`)
*   **Workspace Manager Agent:** An agent that can create, start, stop, and monitor projects in the workspace. (Located in `agents/roles/workspace_manager_agent`)

## Workspace

This project now includes a `workspace` directory where new projects can be created and managed by the `workspace_manager_agent`. This allows for the creation of projects with different technology stacks and runtimes, including Docker-based projects for true environment isolation.

## Workspace

This project now includes a `workspace` directory where new projects can be created and managed by the `workspace_manager_agent`. This allows for the creation of projects with different technology stacks and runtimes, including Docker-based projects for true environment isolation.

## Getting Started

To use these agents, you need to have the Gemini CLI installed and configured. You also need to run the agent web services.

### Running Python-based Agents

1.  Clone this repository.
2.  Install the dependencies for all agents: `pip install -r file_analyzer_agent/requirements.txt && pip install -r web_surfer_agent/requirements.txt && pip install -r ollama_agent/requirements.txt`
3.  Run the `start_agents.sh` script to launch all agents: `./scripts/start_agents.sh`
4.  The agents will be running on ports starting from 8000.

### Running Dockerized Agents

1.  Ensure Docker is installed and running on your system.
2.  **Configure Agents:** Edit `scripts/agents.conf` to uncomment the agent directories you wish to launch.
3.  Run the `parallel_start_dockerized_agents.sh` script to build and launch the configured Dockerized agents: `./scripts/parallel_start_dockerized_agents.sh`
4.  The agents will be running in Docker containers, accessible on automatically assigned ports starting from 8000.
5.  To check the status of running agents, use: `./scripts/check_agent_status.sh`

### General Setup

To make the agents available as tools, copy their OpenAPI specifications to the `.gemini/tools/` directory.

## Session Management

This project includes a simple session management feature to help resume work between sessions. The `session.md` file stores a summary of the last session's state, including the last action taken, the status of any running processes, and the next steps.

To resume a session, simply ask me to "resume", and I will read the `session.md` file to get caught up.

## Development Process

This project follows a structured, role-based development process to ensure quality and consistency. All new features and significant changes are developed by following a "virtual IT team" workflow:

1.  **Product Owner Request:** The user provides a high-level feature request.
2.  **Solution Architect Planning:** I, acting as the Solution Architect, will create a `Feature Brief` from the provided template. This brief outlines the technical approach and the testing strategy.
3.  **Implementation:** Acting as the Coder, I will implement the feature according to the brief.
4.  **Testing:** Acting as the Tester, I will execute the testing plan defined in the brief.
5.  **Definition of Done:** The feature is only considered complete when all criteria in the `DEFINITION_OF_DONE.md` are met.

### Cyclic Error Watchdog

To prevent getting stuck in repetitive, failing loops, I have an internal "Cyclic Error Watchdog" protocol. If I detect that I am repeating the same failing actions, I will automatically interrupt my own process, brainstorm a list of fundamentally different approaches to the problem, and present them to you for a decision.
