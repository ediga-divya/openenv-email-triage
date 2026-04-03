"""
server.py - FastAPI server exposing the OpenEnv HTTP interface.
"""
import os
from pathlib import Path
from fastapi import FastAPI, HTTPException
from fastapi.responses import PlainTextResponse
from pydantic import BaseModel
from email_env import EmailAction, EmailTriageEnv

app = FastAPI(title="Email Triage OpenEnv", version="1.0.0")
_TASK_NAME = os.getenv("EMAIL_TASK", "triage_classify")
_env = EmailTriageEnv(task_name=_TASK_NAME)

class ResetRequest(BaseModel):
    task_name: str = _TASK_NAME

class SetTaskRequest(BaseModel):
    task_name: str

@app.get("/health")
def health():
    return {"status": "ok", "task": _env.task_name}

@app.get("/tasks")
def list_tasks():
    return {"tasks": EmailTriageEnv.TASK_NAMES}

@app.post("/set_task")
def set_task(req: SetTaskRequest):
    global _env
    if req.task_name not in EmailTriageEnv.TASK_NAMES:
        raise HTTPException(status_code=400, detail=f"Unknown task: {req.task_name!r}")
    _env = EmailTriageEnv(task_name=req.task_name)
    obs = _env.reset()
    return obs.model_dump()

@app.post("/reset")
def reset(req: ResetRequest = ResetRequest()):
    global _env
    task = req.task_name
    if task not in EmailTriageEnv.TASK_NAMES:
        raise HTTPException(status_code=400, detail=f"Unknown task: {task!r}")
    if task != _env.task_name:
        _env = EmailTriageEnv(task_name=task)
    obs = _env.reset()
    return obs.model_dump()

@app.post("/step")
def step(action: EmailAction):
    try:
        result = _env.step(action)
        return result.model_dump()
    except RuntimeError as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.get("/state")
def state():
    try:
        s = _env.state()
        return s.model_dump()
    except RuntimeError as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.get("/openenv.yaml", response_class=PlainTextResponse)
def serve_yaml():
    yaml_path = Path(__file__).parent / "openenv.yaml"
    if not yaml_path.exists():
        raise HTTPException(status_code=404, detail="openenv.yaml not found")
    return yaml_path.read_text()

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("server:app", host="0.0.0.0", port=7860, reload=False)
