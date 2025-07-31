from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import requests
import os
import asyncio

app = FastAPI()

SECRET_MANAGER_AGENT_URL = "http://localhost:8002"
GOOGLE_DRIVE_AGENT_URL = "http://localhost:8007"

class SecureCommandRequest(BaseModel):
    command: str
    secrets: dict[str, str] # Maps env_var_name to secret_name

@app.post("/prepare_secure_command")
def prepare_secure_command(request: SecureCommandRequest):
    env_vars_export_string = []

    # Give Secret Manager Agent time to start
    # This sleep is a temporary workaround and should be replaced by a proper health check/retry mechanism
    asyncio.run(asyncio.sleep(2))

    with requests.Session() as client:
        for env_var_name, secret_name in request.secrets.items():
            try:
                print(f"Attempting to retrieve secret '{secret_name}' from {SECRET_MANAGER_AGENT_URL}/secrets/{secret_name}")
                response = client.get(f"{SECRET_MANAGER_AGENT_URL}/secrets/{secret_name}")
                response.raise_for_status()
                secret_data = response.json()
                secret_value = secret_data["value"]

                if env_var_name == "GOOGLE_APPLICATION_CREDENTIALS_JSON":
                    # Send credentials directly to google_drive_agent
                    print(f"Sending credentials to Google Drive Agent: {GOOGLE_DRIVE_AGENT_URL}/set_credentials")
                    gd_response = client.post(f"{GOOGLE_DRIVE_AGENT_URL}/set_credentials", json={"credentials_json": secret_value})
                    gd_response.raise_for_status()
                    print(f"Google Drive Agent credentials set successfully: {gd_response.json()}")
                else:
                    # For other secrets, export as environment variable
                    escaped_secret_value = secret_value.replace("\"", "\\\"")
                    env_vars_export_string.append(f'export {env_var_name}="{escaped_secret_value}"')
                
                print(f"Successfully retrieved secret '{secret_name}'.")
            except requests.exceptions.RequestException as e:
                print(f"Error retrieving secret '{secret_name}': {e}")
                raise HTTPException(status_code=500, detail=f"Network error when connecting to Secret Manager Agent or Google Drive Agent: {e}")
            except Exception as e:
                print(f"An unexpected error occurred: {e}")
                raise HTTPException(status_code=500, detail=f"An unexpected error occurred: {e}")

    full_command = " && ".join(env_vars_export_string + [request.command])

    return {"prepared_command": full_command}

@app.get("/health", summary="Health check endpoint")
def health_check() -> dict:
    """Returns a success message to indicate that the agent is running."""
    return {"status": "ok"}

@app.get("/")
async def read_root():
    return {"message": "Secure Executor Agent is running"}