# Tooling & Execution Environment

The Virtual IT Team "Agency" is a collection of personas and skills. However, to translate these personas into actual code and files on a user's machine, the agents require **Tools**.

## The Problem
Standard LLMs (like generating text via a basic chat interface or raw Ollama) can only output text to a screen. They cannot read a repository, create folders, or write files.

## The Solution: Execution Clients

Depending on the environment the user is running, the agents assume they have access to an "Execution Client" that provides underlying tools.

### 1. Premium AI CLI Tooling (e.g., Gemini CLI / Cursor / Roo Code)
When running within advanced agentic environments, the skills assume they have access to:
- **`view_file` / `read_url`**: To gather context.
- **`write_to_file` / `multi_replace`**: To actually execute the blueprints designed by the Solution Architect.
- **`run_command`**: To execute tests, deploy infrastructure, or start servers.

*Notice:* In these premium environments, the orchestrator is often the AI Sandbox itself.

### 2. The Local "Free" Execution (Ollama + Makefiles)
When the user specifically requests to use **Ollama** to avoid API costs, the tools are severely restricted because Ollama is just a raw model runner.

To solve this, the Agency relies on the **`Makefile Orchestrator`** and the **`Prompt Engineer`**.
- The Prompt Engineer slices tasks into micro-prompts.
- The Makefile Orchestrator writes a `Makefile` that uses standard terminal piping to act as the "tools".

**Example Ollama Pipeline (Simulated Tooling):**
```makefile
generate-backend:
	@echo "Reading architect constraints..."
	@cat docs/architecture/schema.md | ollama run llama3 "Based on this schema, write a FastAPI user_router.py. Output ONLY the python code." > src/routes/user_router.py
```

### 3. Missing Infrastructure (The To-Do List)
As the project evolves, the Agency requires developers to build a dedicated **Ollama CLI Orchestrator** if they wish to move beyond Makefiles. This theoretical tool would natively parse the `SKILL.md` files and provide file I/O tools directly to local Ollama models, creating a truly free clone of premium agentic frameworks.
