import httpx
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

app = FastAPI()

OLLAMA_BASE_URL = "http://localhost:11434"

class GenerateRequest(BaseModel):
    model: str
    prompt: str

@app.get("/api/tags")
async def get_models():
    """
    Get a list of available models from the Ollama API.
    """
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(f"{OLLAMA_BASE_URL}/api/tags")
            response.raise_for_status()
            return response.json()
    except httpx.RequestError as e:
        raise HTTPException(status_code=500, detail=f"Error connecting to Ollama: {e}")

@app.post("/generate")
async def generate(request: GenerateRequest):
    """
    Generate text using a specified model.
    """
    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{OLLAMA_BASE_URL}/api/generate",
                json={"model": request.model, "prompt": request.prompt, "stream": False},
                timeout=60.0,
            )
            response.raise_for_status()
            return response.json()
    except httpx.RequestError as e:
        raise HTTPException(status_code=500, detail=f"Error connecting to Ollama: {e}")
    except httpx.ReadTimeout:
        raise HTTPException(status_code=504, detail="Request to Ollama timed out")

@app.get("/health", summary="Health check endpoint")
def health_check() -> dict:
    """Returns a success message to indicate that the agent is running."""
    return {"status": "ok"}

@app.get("/")
def read_root():
    return {"message": "Ollama Agent is running"}
