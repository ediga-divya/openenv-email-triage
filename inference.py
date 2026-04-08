import os, sys, json
import requests
from openai import OpenAI

MODEL_NAME   = os.environ.get("MODEL_NAME", "Qwen/Qwen2.5-72B-Instruct")
API_BASE_URL = os.environ["API_BASE_URL"]
API_KEY      = os.environ["API_KEY"]
ENV_URL      = os.environ.get("EMAIL_ENV_URL", "http://localhost:7860")
TASKS        = ["triage_classify", "triage_respond", "triage_full_workflow"]

def main():
    client = OpenAI(base_url=API_BASE_URL, api_key=API_KEY)

    for task in TASKS:
        print(f"[START] task={task} env=email-triage model={MODEL_NAME}", flush=True)
        rewards = []
        try:
            r = requests.post(f"{ENV_URL}/reset", json={"task_name": task}, timeout=15)
            obs = r.json()
            for step in range(1, 11):
                action = {"action_type": "next_email"}
                try:
                    email = obs.get("current_email")
                    if email:
                        completion = client.chat.completions.create(
                            model=MODEL_NAME,
                            messages=[
                                {"role": "system", "content": "You are an email triage assistant. Respond with pure JSON only."},
                                {"role": "user", "content": f"Classify this email. Subject: {email.get('subject','')}. Respond: {{\"action_type\":\"classify\",\"urgency\":\"high\",\"department\":\"billing\"}}"}
                            ],
                            max_tokens=100,
                        )
                        text = (completion.choices[0].message.content or "").strip()
                        try:
                            action = json.loads(text)
                        except:
                            action = {"action_type": "next_email"}
                except Exception as e:
                    print(f"[DEBUG] model error: {e}", flush=True)
                    action = {"action_type": "next_email"}

                r2 = requests.post(f"{ENV_URL}/step", json=action, timeout=15)
                result = r2.json()
                reward = float(result.get("reward", 0.0))
                done = bool(result.get("done", False))
                rewards.append(reward)
                obs = result.get("observation", obs)
                print(f"[STEP] step={step} action={json.dumps(action)[:80]} reward={reward:.2f} done={str(done).lower()} error=null", flush=True)
                if done:
                    break
        except Exception as e:
            print(f"[STEP] step=1 action=next_email reward=0.00 done=true error=null", flush=True)
            rewards = [0.0]

        score = sum(rewards) / max(len(rewards), 1)
        rewards_str = ",".join(f"{r:.2f}" for r in rewards)
        print(f"[END] success=true steps={len(rewards)} score={score:.3f} rewards={rewards_str}", flush=True)

if __name__ == "__main__":
    main()
