# Feature Brief: Dockerize Agents

> **Product Owner:** As a project team, I would like to have Dockerized versions of all agents to improve isolation and deployment, and new scripts to manage these Dockerized agents.

## 1. Solution Architect Analysis

**Goal:** To containerize all existing agents using Docker and provide new shell scripts for their management (start, stop, restart).

**Architectural Approach:**
- For each existing agent, a `Dockerfile` will be created in its respective directory.
- Each `Dockerfile` will:
    - Use a suitable base Python image.
    - Copy the agent's code and `requirements.txt`.
    - Install dependencies.
    - Expose the agent's default port (e.g., 8000, 8001, etc.).
    - Define the `CMD` to run the `uvicorn` server.
- A new set of management scripts (`start_dockerized_agents.sh`, `stop_dockerized_agents.sh`, `restart_dockerized_agents.sh`) will be created in the `scripts/` directory.
- `start_dockerized_agents.sh` will:
    - Build Docker images for all agents.
    - Run each agent in a separate Docker container, mapping the internal port to an external host port.
    - Maintain a record of running container IDs or names.
- `stop_dockerized_agents.sh` will stop and remove all running agent containers.
- `restart_dockerized_agents.sh` will combine stop and start functionality.
- The existing `start_agents.sh` and `stop_agents.sh` will remain for the non-Dockerized versions.

**New Files (per agent):**
- `<agent_name>/Dockerfile`

**New Files (global):**
- `scripts/start_dockerized_agents.sh`
- `scripts/stop_dockerized_agents.sh`
- `scripts/restart_dockerized_agents.sh`
- `features/dockerize_agents.md` (this feature brief)

**Artifacts to be Updated:**
- `README.md` (mention Dockerized agents and new scripts)
- `todo.txt` (mark task as in progress/done)
- `session.md` (update to reflect Dockerization development)
- `knowledge.txt` (add Dockerized agents to knowledge base)
- `project_knowledge.md` (update agent descriptions to mention Dockerization)

## 2. Tester Agent Plan

**Testing Strategy:**
- **Unit Tests (Dockerfiles):**
    1.  Build each Docker image individually to ensure it builds successfully.
    2.  Run a container from each image and verify the agent starts and its health endpoint is accessible.
- **Integration Tests (Scripts):**
    1.  Ensure no Docker containers are running.
    2.  Execute `scripts/start_dockerized_agents.sh`.
    3.  Verify that all agent containers are running and their exposed ports are accessible.
    4.  Execute `scripts/stop_dockerized_agents.sh`.
    5.  Verify that all agent containers are stopped and removed.
    6.  Execute `scripts/restart_dockerized_agents.sh` and verify functionality.
    7.  Test calling an agent through the Root Agent when agents are Dockerized.

**Success Criteria:**
- All Docker images build successfully.
- All Dockerized agents start, stop, and restart correctly via the new scripts.
- All Dockerized agents are accessible on their assigned ports.
- The Root Agent can successfully interact with Dockerized agents.
