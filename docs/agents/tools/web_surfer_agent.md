# Web Surfer Agent

## Overview

The Web Surfer Agent provides capabilities to interact with web pages. It can be used to navigate to URLs, take screenshots, and perform actions like clicking elements. This agent is essential for tasks requiring web-based information retrieval or interaction.

## Location

`agents/tools/web_surfer_agent`

## Capabilities

*   **Health Check**: Provides a `/health` endpoint to verify the agent's operational status.
*   **Navigate to URL**: (To be implemented/detailed) Allows the agent to open a specified URL.
*   **Take Screenshot**: (To be implemented/detailed) Captures a screenshot of the current web page.
*   **Click Element**: (To be implemented/detailed) Simulates a click on a specified web element.

## Usage

This agent is useful for tasks that involve browsing the internet, gathering visual information from web pages, or interacting with web applications.

### Example (Conceptual)

Once fully implemented, you might interact with it via the Root Agent:

```python
# Conceptual Python code for calling Web Surfer Agent via Root Agent
from root_agent_client import RootAgentClient

root_client = RootAgentClient(base_url="http://localhost:8005") # Assuming Root Agent is on 8005

# Example: Navigate and take a screenshot (conceptual)
response = await root_client.call_agent(
    agent_name="web_surfer_agent",
    endpoint="navigate",
    method="POST",
    payload={"url": "https://www.example.com"}
)
print(response)

response = await root_client.call_agent(
    agent_name="web_surfer_agent",
    endpoint="screenshot",
    method="GET"
)
print(response)
```

## Development Notes

*   The agent's `main.py` uses FastAPI to expose its API.
*   It will likely integrate with a headless browser automation library (e.g., Playwright, Selenium) to perform web interactions.
