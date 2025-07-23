# /home/cortex/agents_tools/web_surfer_agent/main.py
from fastapi import FastAPI
from pydantic import BaseModel
from playwright.async_api import async_playwright
import asyncio

app = FastAPI(
    title="Web Surfer Agent",
    description="An agent that can interact with web pages.",
    version="1.0.0",
)

class ScreenshotRequest(BaseModel):
    url: str
    path: str

class ClickRequest(BaseModel):
    url: str
    x: int
    y: int

@app.post("/take-screenshot", summary="Take a screenshot of a web page")
async def take_screenshot(request: ScreenshotRequest) -> dict:
    """Takes a screenshot of a web page and saves it to a file."""
    async with async_playwright() as p:
        browser = await p.chromium.launch()
        page = await browser.new_page()
        await page.goto(request.url)
        await page.screenshot(path=request.path)
        await browser.close()
    return {"status": "success", "path": request.path}

@app.post("/click", summary="Click on a web page at a given coordinate")
async def click(request: ClickRequest) -> dict:
    """Clicks on a web page at a given (x, y) coordinate."""
    async with async_playwright() as p:
        browser = await p.chromium.launch()
        page = await browser.new_page()
        await page.goto(request.url)
        await page.mouse.click(request.x, request.y)
        await browser.close()
    return {"status": "success"}

@app.get("/health", summary="Health check endpoint")
async def health_check() -> dict:
    """Returns a success message to indicate that the agent is running."""
    return {"status": "ok"}
