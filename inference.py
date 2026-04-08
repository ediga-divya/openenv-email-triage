import json, os, sys
from typing import List
import requests
from openai import OpenAI

API_KEY      = os.getenv("HF_TOKEN") or os.getenv("API_KEY") or "sk-dummy-key"
API_BASE_URL = os.getenv("API_BASE_URL", "https://router.huggingface.co/v1")
MODEL_NAME   = os.getenv("MODEL_NAME", "Qwen/Qwen2.5-72B-Instruct")
ENV_URL      = os.getenv("EMAIL_ENV_URL", "http://localhost:7860")
MAX_STEPS    = 10
SUCCESS_SCORE_THRESHOLD = 0.4
TASKS = ["triage_classify", "triage_respond", "triage_full_workflow"]

def log_start(task, env, model):
    sys.stdout.write(f"[START] task={task} env={env} model={model}\n")
    sys.stdout.flush()

def log_step(step, action, reward, done, error):
    error_val = error if error else "null"
    done_val = str(done).lower()
    sys.stdout.write(f"[STEP] step={step} action={str(action)[:100]} reward={reward:.2f} done={done_val} error={error_val}\n")
    sys.stdout.flush()

def log_end(success, steps, score, rewards):
    rewards_str = ",".join(f"{r:.2f}" for r in rewards) if rewards else "0.00"
    sys.stdout.write(f"[END] success={str(success).lower()} steps={steps} score={score:.3f} rewards={rewards_str}\n")
    sys.stdout.flush()

def env_reset(task_name):
    try:
        r = requests.post(f"{ENV_URL}/reset", json={"task_name": task_name}, timeout=30)
        r.raise_for_status()
        return r.json()
    except Exception as e:
        sys.stdout.write(f"[DEBUG] env_reset error: {e}\n")
        sys.stdout.flush()
        return None

def env_step(action):
    try:
        r = requests.post(f"{ENV_URL}/step", json=action, timeout=30)
        r.raise_for_status()
        return r.json()
    except Exception as e:
        sys.stdout.write(f"[DEBUG] env_step error: {e}\n")
        sys.stdout.flush()
        return None

def run_episode(client, task_name):
    log_start(task=task_name, env="email-triage", model=MODEL_NAME)
    rewards = []
    steps_taken = 0
    score = 0.0
    success = False

    try:
        obs = env_reset(task_name)
        if obs is None:
            log_step(1, "next_email", 0.0, True, "env_unavailable")
            log_end(False, 1, 0.0, [0.0])
            return 0.0

        done = obs.get("episode_done", False)

        for step in range(1, MAX_STEPS + 1):
            if done:
                break

            action = {"action_type": "next_email"}
            try:
                email = obs.get("current_email")
                if email and client:
                    prompt = f"Email subject: {email.get('subject','')}. Body: {email.get('body','')}. Task: {task_name}. Respond with JSON only: {{\"action_type\":\"classify\",\"urgency\":\"high\",\"department\":\"billing\"}}"
                    completion = client.chat.completions.create(
                        model=MODEL_NAME,
                        messages=[
                            {"role":"system","content":"Respond with pure JSON action only."},
                            {"role":"user","content":prompt}
                        ],
                        temperature=0.2,
                        max_tokens=150,
                    )
                    text = (completion.choices[0].message.content or "").strip()
                    if "```" in text:
                        text = text.split("```")[1]
                        if text.startswith("json"):
                            text = text[4:]
                    action = json.loads(text.strip())
            except Exception as e:
                sys.stdout.write(f"[DEBUG] model error: {e}\n")
                sys.stdout.flush()
                action = {"action_type": "next_email"}

            result = env_step(action)
            if result is None:
                log_step(step, json.dumps(action), 0.0, True, "step_failed")
                rewards.append(0.0)
                steps_taken = step
                break

            reward = float(result.get("reward", 0.0))
            done = bool(result.get("done", False))
            obs = result.get("observation", obs)
            rewards.append(reward)
            steps_taken = step
            log_step(step=step, action=json.dumps(action), reward=reward, done=done, error=None)

        score = min(max(sum(rewards) / MAX_STEPS, 0.0), 1.0)
        success = score >= SUCCESS_SCORE_THRESHOLD

    except Exception as e:
        sys.stdout.write(f"[DEBUG] episode error: {e}\n")
        sys.stdout.flush()
        if not rewards:
            log_step(1, "next_email", 0.0, True, str(e))
            rewards = [0.0]
            steps_taken = 1

    finally:
        log_end(success=success, steps=steps_taken, score=score, rewards=rewards)

    return score

def main():
    client = None
    try:
        client = OpenAI(base_url=API_BASE_URL, api_key=API_KEY)
    except Exception as e:
        sys.stdout.write(f"[DEBUG] client error: {e}\n")
        sys.stdout.flush()

    for task in TASKS:
        run_episode(client, task)

if __name__ == "__main__":
    main()
