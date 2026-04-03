import os, sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))
from fastapi import FastAPI, HTTPException
from fastapi.responses import PlainTextResponse
from pydantic import BaseModel
from email_env import EmailAction, EmailTriageEnv

app = FastAPI(title="Email Triage OpenEnv", version="1.0.0")
_TASK_NAME = os.getenv("EMAIL_TASK", "triage_classify")
_env = EmailTriageEnv(task_name=_TASK_NAME)

class ResetRequest(BaseModel):
    task_name: str = _TASK_NAME

@app.get("/health")
def health():
    return {"status": "ok", "task": _env.task_name}

@app.get("/tasks")
def list_tasks():
    return {"tasks": EmailTriageEnv.TASK_NAMES}

@app.post("/reset")
def reset(req: ResetRequest = ResetRequest()):
    global _env
    if req.task_name != _env.task_name:
        _env = EmailTriageEnv(task_name=req.task_name)
    return _env.reset().model_dump()

@app.post("/step")
def step(action: EmailAction):
    try:
        return _env.step(action).model_dump()
    except RuntimeError as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.get("/state")
def state():
    return _env.state().model_dump()

def main():
    import uvicorn
    uvicorn.run("server.app:app", host="0.0.0.0", port=7860)

if __name__ == "__main__":
    main()