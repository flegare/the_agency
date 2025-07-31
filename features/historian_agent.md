# Feature Brief: Historian Agent

> **Product Owner:** As a project team, I would like an agent that tracks project evolution, actions, and key learnings, archives useful files, and facilitates seamless session resumption.

## 1. Solution Architect Analysis

**Goal:** To create a Historian Agent that tracks project evolution, actions, and key learnings, archives useful files, and facilitates seamless session resumption.

**Architectural Approach:**
- The Historian Agent will be a FastAPI application.
- It will expose endpoints to:
    - `archive_session`: This endpoint will be called at the end of a session. It will take a summary of the session (e.g., from `session.md`), and potentially a list of files to archive. It will store this information in a structured way (e.g., a new `history/` directory with timestamped entries).
    - `load_context`: This endpoint will be called at the beginning of a new session. It will read the latest archived session data and provide relevant context.
- It will interact with the file system to read/write session summaries and archive files.
- It will need to understand the project structure to identify "useful files" for archiving (e.g., `checkpoint.txt`, `session.md`, `todo.txt`, `logs/`, `features/`).
- Consider using a simple JSON or Markdown format for archiving session data.

**New Files:**
- `historian_agent/main.py`
- `historian_agent/requirements.txt`
- `history/` (new directory for archived sessions)
- `features/historian_agent.md` (this feature brief)

**Artifacts to be Updated:**
- `README.md` (add Historian Agent to list of agents)
- `todo.txt` (add Historian Agent development task)
- `scripts/start_agents.sh` (add Historian Agent to launch script)
- `scripts/stop_agents.sh` (add Historian Agent to stop script)
- `session.md` (update to reflect Historian Agent usage for session management)
- `knowledge.txt` (add Historian Agent to knowledge base)

## 2. Tester Agent Plan

**Testing Strategy:**
- **Unit Tests (within agent):** Test the `archive_session` and `load_context` functions with various inputs (empty summaries, lists of files, etc.).
- **Integration Tests (CLI interaction):**
    1.  Start all agents, including the Historian Agent.
    2.  Perform some actions (e.g., generate code with Coder Agent).
    3.  Call the Historian Agent's `archive_session` endpoint with a session summary and relevant files.
    4.  Stop all agents.
    5.  Simulate a new session (e.g., clear `session.md` or create a new one).
    6.  Call the Historian Agent's `load_context` endpoint.
    7.  Verify that the loaded context accurately reflects the archived session.

**Success Criteria:**
- Historian Agent launches successfully.
- `archive_session` successfully creates timestamped archive entries.
- `load_context` successfully retrieves and presents the correct archived session data.
- The process is seamless and provides relevant context for resuming work.
