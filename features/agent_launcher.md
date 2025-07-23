# Feature Brief: Agent Launcher

> **Product Owner:** As a project team, I would like to easily start all agents with one command. Make sure this will be launching all agents we will have added in the future.

## 1. Solution Architect Analysis

**Goal:**
- To create a single, executable script that launches all available agents. The script must be easily extensible to accommodate future agents.

**Architectural Approach:**
- A shell script named `start_agents.sh` will be created in a new `scripts/` directory.
- The script will automatically detect all agent directories (any subdirectory in the root that contains a `requirements.txt` file).
- For each detected agent, the script will:
    1.  Assign a unique port number, starting from a base port (e.g., 8000).
    2.  Launch the `uvicorn` server for that agent in the background.
    3.  Log the agent name and the port it's running on.
- The script will also create a `.agent_pids` file to store the process IDs (PIDs) of the backgrounded agents, making them easier to stop later.

**New Files:**
- `features/agent_launcher.md` (this file)
- `scripts/start_agents.sh`

**Artifacts to be Updated:**
- [ ] `README.md`
- [ ] `todo.txt`
- [ ] `knowledge.txt`
- [ ] `session.md`

## 2. Tester Agent Plan

**Testing Strategy:**
- **Integration Tests:**
    1.  I will first ensure no agents are currently running.
    2.  I will execute the `scripts/start_agents.sh` script.
    3.  I will verify that the script outputs the correct messages, indicating that it has found and started both the `file_analyzer_agent` and the `web_surfer_agent` on ports 8000 and 8001, respectively.
    4.  I will use `curl` to send a request to each agent's health check endpoint (which we will add) to confirm they are responsive.

**Success Criteria:**
- The script executes without errors.
- Both agents are running and responsive on their assigned ports.
- The `.agent_pids` file is created and contains two PIDs.
