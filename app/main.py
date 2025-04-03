from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Optional
from app.models.llm import LLMHandler
from app.utils.prompts import generate_system_prompt, generate_collection_prompt

app = FastAPI(title="Travel Assistant API")
llm_handler = LLMHandler()

class UserInput(BaseModel):
    message: str
    context: Optional[List[dict]] = []

class TravelPreferences(BaseModel):
    destination: Optional[str] = None
    duration: Optional[int] = None
    budget: Optional[float] = None
    interests: Optional[List[str]] = None
    travel_style: Optional[str] = None

@app.get("/")
async def root():
    return {"message": "Welcome to the Travel Assistant API"}

@app.post("/chat")
async def chat_endpoint(user_input: UserInput):
    try:
        response = llm_handler.generate_response(
            user_input.message,
            user_input.context
        )
        return {"response": response}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/generate-itinerary")
async def generate_itinerary(preferences: TravelPreferences):
    try:
        prompt = generate_system_prompt(preferences.dict())
        response = llm_handler.generate_itinerary(prompt)
        return {"itinerary": response}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/get-collection-prompt")
async def get_collection_prompt():
    return {"prompt": generate_collection_prompt()} 