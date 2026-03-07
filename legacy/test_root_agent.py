import pytest
from unittest.mock import AsyncMock, patch
from fastapi.testclient import TestClient
import httpx
from root_agent.main import app

client = TestClient(app)

@pytest.fixture
def mock_httpx_client():
    with patch('httpx.AsyncClient') as mock_client:
        yield mock_client

@pytest.fixture
def mock_list_agents():
    with patch('root_agent.main.list_agents') as mock_list:
        mock_list.return_value = {"agents": [{"name": "test_agent", "port": 8000}]}
        yield mock_list

@pytest.mark.asyncio
async def test_call_agent_success(mock_httpx_client, mock_list_agents):
    mock_response = AsyncMock(spec=httpx.Response)
    mock_response.status_code = 200
    mock_response.json.return_value = {"message": "Agent response"}
    mock_response.raise_for_status.return_value = None
    mock_httpx_client.return_value.__aenter__.return_value.post.return_value = mock_response

    response = client.post(
        "/call_agent",
        json={
            "agent_name": "test_agent",
            "endpoint": "health",
            "method": "POST",
            "payload": {}
        }
    )

    assert response.status_code == 200
    assert response.json() == {"status": "success", "response": {"message": "Agent response"}}
    mock_httpx_client.return_value.__aenter__.return_value.post.assert_called_once()

@pytest.mark.asyncio
async def test_call_agent_network_error(mock_httpx_client, mock_list_agents):
    mock_httpx_client.return_value.__aenter__.return_value.post.side_effect = httpx.RequestError("Network error", request=httpx.Request("POST", "http://localhost"))

    response = client.post(
        "/call_agent",
        json={
            "agent_name": "test_agent",
            "endpoint": "health",
            "method": "POST",
            "payload": {}
        }
    )

    assert response.status_code == 500
    assert "Agent call failed due to network error" in response.json()["detail"]

@pytest.mark.asyncio
async def test_call_agent_http_error(mock_httpx_client, mock_list_agents):
    mock_response = AsyncMock(spec=httpx.Response)
    mock_response.status_code = 404
    mock_response.text = "Not Found"
    mock_response.raise_for_status.side_effect = httpx.HTTPStatusError("Not Found", request=httpx.Request("POST", "http://localhost"), response=mock_response)
    mock_httpx_client.return_value.__aenter__.return_value.post.return_value = mock_response

    response = client.post(
        "/call_agent",
        json={
            "agent_name": "test_agent",
            "endpoint": "nonexistent",
            "method": "POST",
            "payload": {}
        }
    )

    assert response.status_code == 404
    assert "Agent call failed with HTTP error" in response.json()["detail"]

