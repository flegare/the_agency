# Ollama Agent

## Overview

The Ollama Agent provides an interface to interact with a local Ollama instance. Ollama allows you to run large language models (LLMs) locally on your machine. This agent acts as a bridge, enabling other agents or the Gemini CLI to leverage local LLMs for various tasks without needing direct access to the Ollama service.

## Location

`agents/tools/ollama_agent`

## Capabilities

*   **Health Check**: Provides a `/health` endpoint to verify the agent's operational status.
*   **Model Interaction**: (To be implemented/detailed) This agent is designed to facilitate interactions with models served by Ollama, such as generating text, embeddings, or other model-specific operations.

## Usage

To use the Ollama Agent, you must have an Ollama instance running locally. The agent expects to connect to Ollama on its default port (typically 11434).

### Example (Conceptual)

Once fully implemented, you might interact with it via the Root Agent like this:

```python
# Conceptual Python code for calling Ollama Agent via Root Agent
from root_agent_client import RootAgentClient

root_client = RootAgentClient(base_url="http://localhost:8002") # Assuming Root Agent is on 8002

response = await root_client.call_agent(
    agent_name="ollama_agent",
    endpoint="generate", # Example endpoint for text generation
    method="POST",
    payload={"model": "llama2", "prompt": "Tell me a joke."}
)

print(response)
```

## Development Notes

*   The agent's `main.py` uses FastAPI to expose its API.
*   It relies on the `httpx` library for making asynchronous HTTP requests to the Ollama service.
*   Ensure your local Ollama instance is running and accessible from within the Docker container if you are running the Ollama Agent in Docker.
