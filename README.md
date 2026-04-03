# Email Triage OpenEnv

A real-world email triage environment for training and evaluating AI agents.

## Tasks
- triage_classify (easy): classify urgency + department
- triage_respond (medium): classify + draft replies
- triage_full_workflow (hard): full inbox management + summary

## Quick Start
```bash
pip install -r requirements.txt
python test_env.py
uvicorn server:app --port 7860
```

## Inference
```bash
export HF_TOKEN=your_token
export EMAIL_ENV_URL=http://localhost:7860
python inference.py
```
