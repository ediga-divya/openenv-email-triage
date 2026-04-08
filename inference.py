"""
inference.py - Baseline inference script for Email Triage OpenEnv.
ENVIRONMENT VARIABLES REQUIRED:
  API_BASE_URL, MODEL_NAME, HF_TOKEN, EMAIL_ENV_URL
"""
import json, os, sys
from typing import Any, Dict, List, Optional
import requests
from openai import OpenAI

API_KEY      = os.getenv("HF_TOKEN") or os.getenv("API_KEY") or "sk-dummy-key"
API_BASE_URL = os.getenv("API_BASE_URL", "https://router.huggingface.co/v1")
MODEL_NAME   = os.getenv("MODEL_NAME", "Qwen/Qwen2.5-72B-Instruct")
ENV_URL      = os.getenv("EMAIL_ENV_URL", "http://localhost:7860")
TEMPERATURE  = 0.2
MAX_TOKENS   = 512
MAX_STEPS    = 50
SUCCESS_SCORE_THRESHOLD = 0.4
TASKS = ["triage_classify", "triage_respond", "triage_full_workflow"]

def log_start(task, env, model):
    print(f"[START] task={task} env={env} model={model}", flush=True)

def log_step(step, action, reward, done, error):
    error_val = error if error else "null"
    print(f"[STEP] step={step} action={str(action)[:200].replace(chr(10),' ')} reward={reward:.2f} done={str(done).lower()} error={error_val}", flush=True)

def log_end(success, steps, score, rewards):
    rewards_str = ",".join(f"{r:.2f}" for r in rewards)
    print(f"[END] success={str(success).lower()} steps={steps} score={score:.3f} rewards={rewards_str}", flush=True)

def env_reset(task_name):
    try:
        r = requests.post(f"{ENV_URL}/reset", json={"task_name": task_name}, timeout=30)
        r.raise_for_status()
        return r.json()
    except Exception as e:
        print(f"[DEBUG] env_reset error: {e}", flush=True)
        return {"episode_done": True, "inbox_stats": {}}

def env_step(action):
    try:
        r = requests.post(f"{ENV_URL}/step", json=action, timeout=30)
        r.raise_for_status()
        return r.json()
    except Exception as e:
        print(f"[DEBUG] env_step error: {e}", flush=True)
        return {"reward": 0.0, "done": True, "observation": {}, "info": {}}

SYSTEM_PROMPT = """You are an expert email triage assistant. Respond with a single JSON object only - no markdown, no code fences.

action_type options:
- classify: {"action_type":"classify","urgency":"critical","department":"billing"}
- respond: {"action_type":"respond","reply_text":"Dear ..."}
- escalate: {"action_type":"escalate","should_escalate":true,"reason":"..."}
- mark_spam: {"action_type":"mark_spam","is_spam":false}
- next_email: {"action_type":"next_email"}
- summarize: {"action_type":"summarize","summary_text":"...","critical_count":3,"spam_count":1,"escalated_count":3}

Rules: Pure JSON only. Never reply to spam. Complete required actions before next_email."""

def get_model_action(client, obs, task_name, history):
    try:
        email = obs.get("current_email")
        stats = obs.get("inbox_stats", {})
        email_block = "No current email."
        if email:
            email_block = f"ID: {email['id']}\nFrom: {email['sender']}\nSubject: {email['subject']}\nBody: {email['body']}"
        prompt = f"TASK: {task_name}\nSTEP: {obs.get('step_number','?')}\n\nEMAIL:\n{email_block}\n\nSTATS: {stats}\nFEEDBACK: {obs.get('last_action_feedback','')}\nVALID ACTIONS: {obs.get('valid_actions',[])}\n\nRespond with JSON action:"
        completion = client.chat.completions.create(
            model=MODEL_NAME,
            messages=[{"role":"system","content":SYSTEM_PROMPT},{"role":"user","content":prompt}],
            temperature=TEMPERATURE, max_tokens=MAX_TOKENS, stream=False,
        )
        text = (completion.choices[0].message.content or "").strip()
        if text.startswith("```"):
            text = text.split("```")[1]
            if text.startswith("json"):
                text = text[4:]
        return json.loads(text.strip())
    except Exception as e:
        print(f"[DEBUG] Model error: {e}", flush=True)
        return {"action_type": "next_email"}

def run_episode(client, task_name):
    log_start(task=task_name, env="email-triage", model=MODEL_NAME)
    rewards, steps_taken, score, success = [], 0, 0.0, False
    history = []
    try:
        obs = env_reset(task_name)
        done = obs.get("episode_done", False)
        for step in range(1, MAX_STEPS + 1):
            if done:
                break
            action = get_model_action(client, obs, task_name, history)
            action_str = json.dumps(action)
            result = env_step(action)
            reward = float(result.get("reward", 0.0))
            done   = bool(result.get("done", False))
            obs    = result.get("observation", obs)
            rewards.append(reward)
            steps_taken = step
            log_step(step=step, action=action_str, reward=reward, done=done, error=None)
            history.append(f"Step {step}: {action_str[:80]} -> reward={reward:.2f}")
        score = min(max(float(sum(rewards)) / MAX_STEPS, 0.0), 1.0)
        success = score >= SUCCESS_SCORE_THRESHOLD
    except Exception as e:
        print(f"[DEBUG] Episode error: {e}", flush=True)
    finally:
        log_end(success=success, steps=steps_taken, score=score, rewards=rewards)
    return score

def main():
    try:
        client = OpenAI(base_url=API_BASE_URL, api_key=API_KEY)
    except Exception as e:
        print(f"[DEBUG] OpenAI client error: {e}", flush=True)
        sys.exit(0)
    task_arg = os.getenv("EMAIL_TASK", "all")
    tasks_to_run = TASKS if task_arg == "all" else [task_arg]
    scores = {}
    for task in tasks_to_run:
        print(f"\n{'='*60}\nRunning task: {task}\n{'='*60}", flush=True)
        scores[task] = run_episode(client, task)
        print(f"[SUMMARY] task={task} score={scores[task]:.3f}", flush=True)
    print("\n[FINAL SCORES]", flush=True)
    for task, s in scores.items():
        print(f"  {task}: {s:.3f}", flush=True)
    overall = sum(scores.values()) / len(scores) if scores else 0.0
    print(f"  OVERALL: {overall:.3f}", flush=True)

if __name__ == "__main__":
    main()
