# Secret Manager Agent

## Overview

The Secret Manager Agent is responsible for securely managing secrets and sensitive information within the Gemini CLI agent ecosystem. It provides capabilities to create, store, and retrieve secret values, ensuring that sensitive data is not exposed directly in code or logs. This agent is crucial for maintaining the security posture of the entire system.

## Location

`agents/tools/secret_manager_agent`

## Capabilities

*   **Health Check**: Provides a `/health` endpoint to verify the agent's operational status.
*   **Secret Creation**: (To be implemented/detailed) Allows for the creation of new secret containers.
*   **Secret Versioning**: (To be implemented/detailed) Supports adding new versions to existing secrets.
*   **Secret Retrieval**: (To be implemented/detailed) Enables secure retrieval of secret values.

## Usage

The Secret Manager Agent is typically used by other agents (e.g., `secure_executor_agent`) that require access to sensitive information. It ensures that secrets are injected into processes securely without direct exposure to the LLM.

### Example (Conceptual)

Once fully implemented, you might interact with it via the Root Agent for secret management:

```python
# Conceptual Python code for calling Secret Manager Agent via Root Agent
from root_agent_client import RootAgentClient

root_client = RootAgentClient(base_url="http://localhost:8003") # Assuming Root Agent is on 8003

# Example: Create a secret (conceptual)
response = await root_client.call_agent(
    agent_name="secret_manager_agent",
    endpoint="create_secret",
    method="POST",
    payload={"name": "my_api_key", "value": "super_secret_value"}
)
print(response)

# Example: Retrieve a secret (conceptual)
response = await root_client.call_agent(
    agent_name="secret_manager_agent",
    endpoint="get_secret",
    method="GET",
    payload={"name": "my_api_key"}
)

print(response)
```

## Development Notes

*   The agent's `main.py` uses FastAPI to expose its API.
*   It is designed to integrate with a secure secret management service (e.g., Google Cloud Secret Manager, AWS Secrets Manager, HashiCorp Vault) for production-grade secret handling.
