from fastapi import FastAPI, HTTPException
from typing import List, Dict, Any
from openai import BaseModel
import json
from graph import run_graph
import uvicorn

app = FastAPI()

@app.get("/")
def read_root():
    return {"message": "Hello from FastAPI on your VM!"}

class ChatRequest(BaseModel):
    question: str

@app.post("/search")
async def chat_endpoint(request: ChatRequest):
    result = await run_graph(request.question)
    print(json.dumps(result["final_answer"], indent=4))
    with open("result.json", "w") as f:
        json.dump(result["final_answer"], f, indent=4)
    return {"response": result}


if __name__ == "__main__":
    uvicorn.run(
        "main:app",  # String reference instead of app object
        host="0.0.0.0",
        port=8000,
        reload=True
    )