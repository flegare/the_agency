# Feature Brief: Ollama Agent

> **Product Owner:** As a project team, I would like to make an agent that will call the local end point of ollama. This would be used to when im low on budget for the execution of the work. Ideally build a root agent that will leverage tools we made and can take over project creation if needed. There is a bunch of models installed on local ollama

## 1. Solution Architect Analysis

**Goal:**
- To create a new agent, `ollama_agent`, that can interface with a local Ollama instance. This will allow for the use of local language models as a cost-effective alternative.
- The agent will provide endpoints to list available local models and to generate text using a specified model.

**Architectural Approach:**
- The agent will be a new FastAPI application, consistent with the existing agent architecture.
- It will use the `httpx` library to communicate with the local Ollama API (typically at `http://localhost:11434`).
- The agent will be structured in a new `ollama_agent/` directory.

**New Files:**
- `features/ollama_agent.md` (this file)
- `ollama_agent/main.py`
- `ollama_agent/requirements.txt`

**Artifacts to be Updated:**
- [ ] `README.md`
- [ ] `todo.txt`
- [ ] `knowledge.txt`
- [ ] `session.md`
- [ ] `scripts/start_agents.sh`

## 2. Tester Agent Plan

**Testing Strategy:**
- **Integration Tests:**
    1.  I will update the `scripts/start_agents.sh` script to include the new `ollama_agent`.
    2.  After launching the agents, I will use `curl` to call the new agent's `/models` endpoint to verify it can list the available Ollama models.
    3.  I will then use `curl` to call the `/generate` endpoint, sending a prompt to a specific model and verifying that a response is received.

**Success Criteria:**
- The `ollama_agent` starts without errors.
- The `/models` endpoint returns a list of models from the local Ollama instance.
- The `/generate` endpoint successfully returns a generated response from a specified model.
