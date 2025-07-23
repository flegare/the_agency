# /home/cortex/agents_tools/secret_manager_agent/main.py
import os
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from google.cloud import secretmanager

app = FastAPI(
    title="Secret Manager Agent",
    description="An agent that securely manages secrets using Google Secret Manager.",
    version="1.0.0",
)

# --- Configuration ---
PROJECT_ID = "projectgenerator-hackathon"

# --- Pydantic Models ---
class SecretCreateRequest(BaseModel):
    secret_name: str

# --- Helper Functions ---
def get_secret_client():
    return secretmanager.SecretManagerServiceClient()

# --- API Endpoints ---
@app.post("/secrets", summary="Create a new, empty secret container")
def create_secret(request: SecretCreateRequest):
    client = get_secret_client()
    parent = f"projects/{PROJECT_ID}"
    secret_id = request.secret_name

    try:
        client.create_secret(
            request={"parent": parent, "secret_id": secret_id, "secret": {"replication": {"automatic": {}}}}
        )
        gcloud_command = f'echo "PASTE_YOUR_SECRET_HERE" | gcloud secrets versions add {secret_id} --data-file=-'
        return {
            "status": f"Empty secret '{secret_id}' created.",
            "next_step": "Please run the following command in your local terminal to add the secret value:",
            "command": gcloud_command
        }
    except Exception as e:
        raise HTTPException(status_code=409, detail=f"Secret '{secret_id}' likely already exists. Error: {e}")

@app.get("/secrets/{secret_name}", summary="Get the value of a secret")
def get_secret(secret_name: str):
    client = get_secret_client()
    name = f"projects/{PROJECT_ID}/secrets/{secret_name}/versions/latest"

    try:
        response = client.access_secret_version(request={"name": name})
        payload = response.payload.data.decode("UTF-8")
        return {"secret_name": secret_name, "value": payload}
    except Exception as e:
        raise HTTPException(status_code=404, detail=f"Secret '{secret_name}' not found or could not be accessed. Error: {e}")

@app.delete("/secrets/{secret_name}", summary="Delete a secret")
def delete_secret(secret_name: str):
    client = get_secret_client()
    name = f"projects/{PROJECT_ID}/secrets/{secret_name}"

    try:
        client.delete_secret(request={"name": name})
        return {"status": f"Secret '{secret_name}' deleted."}
    except Exception as e:
        raise HTTPException(status_code=404, detail=f"Secret '{secret_name}' not found or could not be deleted. Error: {e}")

@app.get("/health", summary="Health check endpoint")
def health_check() -> dict:
    """Returns a success message to indicate that the agent is running."""
    return {"status": "ok"}
