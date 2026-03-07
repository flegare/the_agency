import pytest
import requests

# Assuming the agent is running on localhost and port 8002
SECRET_MANAGER_AGENT_URL = "http://localhost:8002"

def test_secret_manager_agent_health_check():
    """
    Tests the health check endpoint of the Secret Manager Agent.
    """
    try:
        response = requests.get(f"{SECRET_MANAGER_AGENT_URL}/health")
        response.raise_for_status()  # Raise an exception for HTTP errors (4xx or 5xx)
        assert response.json() == {"status": "ok"}
    except requests.exceptions.ConnectionError as e:
        pytest.fail(f"Could not connect to Secret Manager Agent at {SECRET_MANAGER_AGENT_URL}. Is it running? Error: {e}")
    except Exception as e:
        pytest.fail(f"An unexpected error occurred during health check: {e}")
