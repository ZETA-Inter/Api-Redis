from fastapi import FastAPI, Query
import redis
import os
from pydantic import BaseModel

class StepRequest(BaseModel):
    worker_id: int
    program_id: int
    step: int

app = FastAPI()

REDIS_URL = os.getenv("REDIS_URL")
r = redis.from_url(REDIS_URL, decode_responses=True)

@app.get("/get_step")
def get_step(
    worker_id: int = Query(..., alias="workerId"),
    program_id: int = Query(..., alias="programId")
):
    try:
        key = f"worker:{worker_id}:program:{program_id}:step"
        retorno = r.get(key)
        if retorno is not None:
            return {"key": key, "value": retorno}
        return {"status": 404, "value": "Chave não encontrada!"}
    except Exception as e:
        return {"status": 500, "error": str(e)}

@app.post("/save-step")
def save_step(request: StepRequest):
    try:
        key = f"worker:{request.worker_id}:program:{request.program_id}:step"
        exists = r.get(key)
        if exists is not None and int(exists) >= request.step:
            return {"status": "ok"}
        r.set(key, request.step)
        return {"status": "ok"}
    except Exception as e:
        return {"status": 500, "error": str(e)}