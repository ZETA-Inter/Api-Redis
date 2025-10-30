from fastapi import FastAPI, Query
from pydantic import BaseModel
import redis
import os

app = FastAPI()

REDIS_URL = os.getenv("REDIS_URL")
r = redis.from_url(REDIS_URL, decode_responses=True)

class StepRequest(BaseModel):
    worker_id: int
    program_id: int
    step: int

@app.get("/get-step")
def get_step(
    worker_id: int = Query(..., alias="workerId"),
    program_id: int = Query(..., alias="programId")
):
    try:
        key = f"worker:{worker_id}:program:{program_id}:step"
        value = r.get(key)

        if value is None:
            return {"status": 404, "value": "Chave não encontrada!"}

        return {"status": 200, "key": key, "value": value}
    
    except Exception as e:
        return {"status": 500, "error": str(e)}

@app.post("/save-step")
def save_step(request: StepRequest):
    try:
        key = f"worker:{request.worker_id}:program:{request.program_id}:step"
        current = r.get(key)

        if current is not None and int(current) >= request.step:
            return {"status": 200}

        r.set(key, request.step)
        return {"status": 200}

    except Exception as e:
        return {"status": 500, "error": str(e)}