from fastapi import FastAPI, Query
import redis
import os
from pydantic import BaseModel

class StepRequest(BaseModel):
    worker_id: int
    program_id: int
    step: int

app = FastAPI()

REDIS_HOST = os.getenv("REDIS_HOST", "redis")
REDIS_PORT = int(os.getenv("REDIS_PORT", "6379"))
REDIS_PASSWORD = os.getenv("REDIS_PASSWORD")

r = redis.Redis(
    host=REDIS_HOST,
    port=REDIS_PORT,
    password=REDIS_PASSWORD,
    decode_responses=True
)

@app.get("/get_step")
def get_step(
    worker_id: int = Query(..., alias="workerId"),
    program_id: int = Query(..., alias="programId")
):
    try:
        key = "worker:"+ str(worker_id) + ":program:" + str(program_id) + ":step"
        retorno = r.get(key)
        if retorno is None:
            return {"status": 404, "value": "Chave não encontrada!"}
        return {"key": key, "value": retorno}
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
        return {"status": 500, "value": str(e)}