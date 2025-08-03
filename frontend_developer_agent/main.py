

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

app = FastAPI()

class ReactComponentRequest(BaseModel):
    component_name: str
    props: list[str] = []

@app.post("/generate_react_component")
async def generate_react_component(request: ReactComponentRequest):
    props_str = ", ".join(request.props)
        component_code = f"""
import React from 'react';

interface {request.component_name}Props {{
  {'
  '.join([f'{prop}: any' for prop in request.props])}
}}

const {request.component_name}: React.FC<{request.component_name}Props> = ({{
  {props_str}
}}) => {{
  return (
    <div>
      <h1>{request.component_name} Component</h1>
      {request.props and <p>Props: {props_str}</p>}
    </div>
  );
}};

export default {request.component_name};
"""
    return {"message": "React component generated successfully", "component_code": component_code}

@app.get("/health")
async def health_check():
    return {"status": "ok"}

