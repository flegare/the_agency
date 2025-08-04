# Secure Executor Agent

## Overview

The Secure Executor Agent is designed to execute shell commands in a controlled and secure environment. Its primary function is to act as an intermediary for commands that might require sensitive information (like API keys or credentials) without exposing that information directly to the command-line interface or logs. It works in conjunction with the Secret Manager Agent to inject secrets as environment variables before command execution.

## Location

`agents/tools/secure_executor_agent`

## Capabilities

*   **Health Check**: Provides a `/health` endpoint to verify the agent's operational status.
*   **Secure Command Execution**: (To be implemented/detailed) Executes shell commands.
*   **Secret Injection**: (To be implemented/detailed) Injects secrets retrieved from the Secret Manager Agent as environment variables into the execution environment of the command.

## Usage

This agent is typically called by other agents that need to run shell commands, especially those requiring access to sensitive data. It ensures that the LLM does not directly handle or see the secret values.

### Example (Conceptual)

Once fully implemented, you might interact with it via the Root Agent:

```python
# Conceptual Python code for calling Secure Executor Agent via Root Agent
from root_agent_client import RootAgentClient

root_client = RootAgentClient(base_url="http://localhost:8004") # Assuming Root Agent is on 8004

# Example: Execute a command with a secret (conceptual)
response = await root_client.call_agent(
    agent_name="secure_executor_agent",
    endpoint="execute_command",
    method="POST",
    payload={
        "command": "curl -H \"Authorization: Bearer $MY_API_KEY\" https://api.example.com/data",
        "secrets": {"MY_API_KEY": "my_api_key_secret_name"} # "my_api_key_secret_name" refers to a secret managed by Secret Manager Agent
    }
)
print(response)
```

## Development Notes

*   The agent's `main.py` uses FastAPI to expose its API.
*   It will likely use Python's `subprocess` module for command execution.
*   Careful consideration of security best practices (e.g., input sanitization, least privilege) is paramount for this agent.

