from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel
import requests
from typing import Dict, Any, List
import uvicorn
import os

app = FastAPI(title="Doctor.AI", description="A modular healthcare assistant system")

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static files
app.mount("/static", StaticFiles(directory="static"), name="static")

# Agent endpoints
AGENT_ENDPOINTS = {
    "patient_info": "http://localhost:5001/a2a",
    "diagnostic": "http://localhost:5002/a2a",
    "medication": "http://localhost:5003/a2a",
    "referral_diet": "http://localhost:5004/a2a"
}

class PatientInput(BaseModel):
    text: str

class AgentResponse(BaseModel):
    agent_type: str
    response: Dict[str, Any]

@app.get("/")
async def root():
    return FileResponse('static/index.html')

@app.get("/health")
async def health_check():
    return {"status": "healthy"}

def call_agent(endpoint: str, text: str) -> Dict[str, Any]:
    try:
        # Clean the input text
        clean_text = text.replace('\\n', '\n').strip()
        print(f"Sending to {endpoint}:")
        print(clean_text)
        
        payload = {
            "content": {
                "text": clean_text
            }
        }
        
        response = requests.post(
            endpoint,
            json=payload,
            timeout=10
        )
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        raise HTTPException(status_code=503, detail=f"Agent service unavailable: {str(e)}")

@app.post("/analyze", response_model=List[AgentResponse])
async def analyze_patient_input(input_data: PatientInput):
    responses = []
    print(f"Received input:")
    print(input_data.text)
    
    # Call each agent in parallel (in a production environment)
    for agent_type, endpoint in AGENT_ENDPOINTS.items():
        try:
            response = call_agent(endpoint, input_data.text)
            responses.append(AgentResponse(
                agent_type=agent_type,
                response=response
            ))
        except HTTPException as e:
            # Log the error but continue with other agents
            print(f"Error calling {agent_type} agent: {str(e)}")
            continue

    if not responses:
        raise HTTPException(status_code=503, detail="All agent services are unavailable")

    return responses

if __name__ == "__main__":
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True) 