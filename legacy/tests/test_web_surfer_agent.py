import pytest
import requests

# Assuming the agent is running on localhost and port 8004
WEB_SURFER_AGENT_URL = "http://localhost:8004"

def test_web_surfer_agent_health_check():
    """
    Tests the health check endpoint of the Web Surfer Agent.
    """
    try:
        response = requests.get(f"{WEB_SURFER_AGENT_URL}/health")
        response.raise_for_status()  # Raise an exception for HTTP errors (4xx or 5xx)
        assert response.json() == {"status": "ok"}
    except requests.exceptions.ConnectionError as e:
        pytest.fail(f"Could not connect to Web Surfer Agent at {WEB_SURFER_AGENT_URL}. Is it running? Error: {e}")
    except Exception as e:
        pytest.fail(f"An unexpected error occurred during health check: {e}")
