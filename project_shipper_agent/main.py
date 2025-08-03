
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import datetime

app = FastAPI()

class LaunchPlanRequest(BaseModel):
    feature_name: str
    launch_date: datetime.date
    target_audience: str
    key_message: str
    success_metrics: list[str]
    rollout_plan: str
    risk_mitigation: str

@app.post("/create_launch_plan")
async def create_launch_plan(request: LaunchPlanRequest):
    # In a real scenario, this would interact with a project management system
    # or generate a detailed document. For now, we'll return a summary.
    plan_summary = f"""
    Launch Plan for: {request.feature_name}
    Launch Date: {request.launch_date}
    Target Audience: {request.target_audience}
    Key Message: {request.key_message}
    Success Metrics: {', '.join(request.success_metrics)}
    Rollout Plan: {request.rollout_plan}
    Risk Mitigation: {request.risk_mitigation}

    This plan outlines the key aspects for a successful launch.
    """
    return {"message": "Launch plan created successfully", "plan_summary": plan_summary}

@app.get("/health")
async def health_check():
    return {"status": "ok"}

