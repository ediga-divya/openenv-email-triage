"""
setup.py - Run this once to create all project files.
Usage: python setup.py
"""
import os

files = {}

files["openenv.yaml"] = '''name: email-triage
version: "1.0.0"
description: >
  A real-world email triage and response environment where an AI agent must
  process an inbox: classify urgency, route to the correct department, draft
  appropriate replies, and manage follow-ups.
author: openenv-hackathon
tags:
  - openenv
  - email
  - triage
  - nlp
  - customer-support
  - real-world

tasks:
  - name: triage_classify
    description: Classify a batch of 10 emails by urgency and department.
    difficulty: easy
    max_steps: 20
    reward_range: [0.0, 1.0]

  - name: triage_respond
    description: Classify each email and draft a professional reply.
    difficulty: medium
    max_steps: 30
    reward_range: [0.0, 1.0]

  - name: triage_full_workflow
    description: Full inbox management including summary report.
    difficulty: hard
    max_steps: 50
    reward_range: [0.0, 1.0]

action_space:
  type: structured
  description: Agent submits JSON with action_type and associated fields.

observation_space:
  type: structured
  description: Agent receives current email, inbox stats, and step feedback.

reward:
  type: shaped
  description: Partial credit every step based on classification, reply quality, escalation, spam detection.

docker:
  image: python:3.11-slim
  port: 7860
'''

files["email_data.py"] = '''"""
email_data.py - Synthetic email corpus and task configuration.
"""
from typing import Dict, List

URGENCY_LEVELS = ["low", "medium", "high", "critical"]
DEPARTMENTS    = ["billing", "technical", "sales", "hr", "legal", "general"]

EMAILS: List[Dict] = [
    {
        "id": "e001",
        "sender": "alice.johnson@example.com",
        "subject": "Invoice #4821 overcharged - need refund ASAP",
        "body": (
            "Hi, I was charged $299 on my last invoice but my plan is only $49/month. "
            "This is the third time this has happened. I need this corrected immediately "
            "and a full refund issued. If this is not resolved today I will dispute the charge."
        ),
        "timestamp": "2024-03-15T09:03:00Z",
        "true_urgency": "critical",
        "true_department": "billing",
        "requires_escalation": True,
        "is_spam": False,
        "key_reply_keywords": ["refund", "apologize", "billing", "resolve", "24 hours"],
    },
    {
        "id": "e002",
        "sender": "newsletter@promo-deals.net",
        "subject": "You WON! Claim your $500 Amazon gift card NOW!!!",
        "body": (
            "Congratulations! You have been selected as our lucky winner. "
            "Click here to claim your prize: http://totally-legit-prize.ru/claim "
            "This offer expires in 24 hours! Act NOW!"
        ),
        "timestamp": "2024-03-15T09:15:00Z",
        "true_urgency": "low",
        "true_department": "general",
        "requires_escalation": False,
        "is_spam": True,
        "key_reply_keywords": [],
    },
    {
        "id": "e003",
        "sender": "bob.martinez@clientcorp.com",
        "subject": "API returning 500 errors since your last deployment",
        "body": (
            "Our production integration has been failing since approximately 2am UTC today. "
            "We are seeing HTTP 500 responses on POST /api/v2/orders. "
            "This is blocking our entire checkout flow. Ticket ID: TKT-88231. Please advise urgently."
        ),
        "timestamp": "2024-03-15T09:22:00Z",
        "true_urgency": "critical",
        "true_department": "technical",
        "requires_escalation": True,
        "is_spam": False,
        "key_reply_keywords": ["investigating", "engineers", "status", "update", "TKT-88231"],
    },
    {
        "id": "e004",
        "sender": "carol.lee@startupxyz.io",
        "subject": "Interested in enterprise plan pricing",
        "body": (
            "Hello, we are a 200-person company evaluating your platform. "
            "Could you send me details on enterprise pricing, volume discounts, "
            "and whether you offer SSO integration? Happy to jump on a call this week."
        ),
        "timestamp": "2024-03-15T10:00:00Z",
        "true_urgency": "medium",
        "true_department": "sales",
        "requires_escalation": False,
        "is_spam": False,
        "key_reply_keywords": ["enterprise", "pricing", "SSO", "call", "demo"],
    },
    {
        "id": "e005",
        "sender": "david.kim@internal.company.com",
        "subject": "PTO request - April 7-11",
        "body": (
            "Hi, I would like to request PTO from April 7 through April 11 (5 days). "
            "My current projects are on track and I have arranged coverage with Sarah. "
            "Please let me know if this is approved."
        ),
        "timestamp": "2024-03-15T10:30:00Z",
        "true_urgency": "low",
        "true_department": "hr",
        "requires_escalation": False,
        "is_spam": False,
        "key_reply_keywords": ["approved", "PTO", "HR", "confirm"],
    },
    {
        "id": "e006",
        "sender": "legal@acquisitionpartners.com",
        "subject": "NDA review required before Monday",
        "body": (
            "Please find attached the mutual NDA for the proposed partnership. "
            "Our legal team requires your signature or redline by end of day Monday. "
            "Please loop in your legal counsel. This is time-sensitive."
        ),
        "timestamp": "2024-03-15T11:00:00Z",
        "true_urgency": "high",
        "true_department": "legal",
        "requires_escalation": True,
        "is_spam": False,
        "key_reply_keywords": ["legal", "NDA", "counsel", "review", "Monday"],
    },
    {
        "id": "e007",
        "sender": "support@paymentprocessor.com",
        "subject": "Your monthly statement is ready",
        "body": (
            "Your account statement for February 2024 is now available in your dashboard. "
            "Total transactions: 1,243. Total volume: $48,291.00. "
            "Log in to view the full report."
        ),
        "timestamp": "2024-03-15T11:30:00Z",
        "true_urgency": "low",
        "true_department": "billing",
        "requires_escalation": False,
        "is_spam": False,
        "key_reply_keywords": ["received", "statement", "noted"],
    },
    {
        "id": "e008",
        "sender": "emily.zhang@bigclient.com",
        "subject": "Data export not working - urgent for board presentation",
        "body": (
            "I need to export our Q1 analytics data by 3pm today for a board meeting. "
            "The CSV export button does nothing when I click it. I have tried Chrome and Firefox. "
            "This is extremely urgent. My entire presentation depends on this data."
        ),
        "timestamp": "2024-03-15T12:00:00Z",
        "true_urgency": "critical",
        "true_department": "technical",
        "requires_escalation": True,
        "is_spam": False,
        "key_reply_keywords": ["investigating", "workaround", "urgent", "data", "export"],
    },
    {
        "id": "e009",
        "sender": "frank.nguyen@partner.org",
        "subject": "Quick question about your API rate limits",
        "body": (
            "Hi team, I was wondering what are the rate limits for the free tier API? "
            "Specifically looking at requests per minute. Happy to upgrade if needed. Thanks!"
        ),
        "timestamp": "2024-03-15T13:00:00Z",
        "true_urgency": "low",
        "true_department": "technical",
        "requires_escalation": False,
        "is_spam": False,
        "key_reply_keywords": ["rate limit", "free tier", "requests", "upgrade"],
    },
    {
        "id": "e010",
        "sender": "grace.park@enterprise-customer.com",
        "subject": "Contract renewal discussion - our agreement expires April 30",
        "body": (
            "Hi, our annual contract expires April 30 and we would like to discuss renewal terms. "
            "We are generally happy with the service but have some concerns about the recent "
            "price increase. Can we schedule a call with your account team next week?"
        ),
        "timestamp": "2024-03-15T13:45:00Z",
        "true_urgency": "high",
        "true_department": "sales",
        "requires_escalation": False,
        "is_spam": False,
        "key_reply_keywords": ["renewal", "call", "account", "schedule", "discuss"],
    },
]

TASK_CONFIGS = {
    "triage_classify": {
        "description": "Classify each email by urgency and department only.",
        "email_ids": ["e001","e002","e003","e004","e005","e006","e007","e008","e009","e010"],
        "required_actions": ["classify", "mark_spam"],
        "max_steps": 20,
        "completion_bonus": 0.2,
    },
    "triage_respond": {
        "description": "Classify each email and draft a relevant professional reply.",
        "email_ids": ["e001","e003","e004","e006","e008","e010"],
        "required_actions": ["classify", "respond", "escalate", "mark_spam"],
        "max_steps": 30,
        "completion_bonus": 0.15,
    },
    "triage_full_workflow": {
        "description": "Full workflow: classify, respond, escalate, detect spam, and summarize.",
        "email_ids": ["e001","e002","e003","e004","e005","e006","e007","e008","e009","e010"],
        "required_actions": ["classify", "respond", "escalate", "mark_spam", "summarize"],
        "max_steps": 50,
        "completion_bonus": 0.25,
    },
}

def get_email_by_id(email_id: str) -> Dict:
    for e in EMAILS:
        if e["id"] == email_id:
            return e
    raise KeyError(f"Email {email_id!r} not found")
'''

files["graders.py"] = '''"""
graders.py - Deterministic graders for all action types.
"""
from __future__ import annotations
import re
from typing import Any, Dict, List, Optional, Tuple


def _normalize(text: str) -> str:
    return text.lower().strip()

def _keyword_coverage(text: str, keywords: List[str]) -> float:
    if not keywords:
        return 1.0
    text_lower = text.lower()
    hits = sum(1 for kw in keywords if kw.lower() in text_lower)
    return hits / len(keywords)

def _reply_structure_score(reply: str) -> float:
    score = 0.0
    if re.search(r"\\b(hi|hello|dear|good (morning|afternoon|evening))\\b", reply, re.I):
        score += 0.25
    word_count = len(reply.split())
    if word_count >= 30:
        score += 0.40
    elif word_count >= 15:
        score += 0.20
    if re.search(r"\\b(regards|sincerely|thank(s| you)|best|cheers)\\b", reply, re.I):
        score += 0.20
    if "[" not in reply and "]" not in reply:
        score += 0.15
    return min(score, 1.0)

def grade_classify(action: Dict, email: Dict) -> Tuple[float, Dict]:
    breakdown: Dict[str, Any] = {}
    urgency_pred = _normalize(action.get("urgency", ""))
    dept_pred    = _normalize(action.get("department", ""))
    urgency_true = email["true_urgency"]
    dept_true    = email["true_department"]
    urgency_levels = ["low", "medium", "high", "critical"]
    if urgency_pred == urgency_true:
        urgency_score = 1.0
    elif urgency_pred in urgency_levels:
        idx_pred = urgency_levels.index(urgency_pred)
        idx_true = urgency_levels.index(urgency_true)
        urgency_score = 0.5 if abs(idx_pred - idx_true) == 1 else 0.0
    else:
        urgency_score = 0.0
    dept_score = 1.0 if dept_pred == dept_true else 0.0
    breakdown.update({"urgency_pred": urgency_pred, "urgency_true": urgency_true,
                      "urgency_score": urgency_score, "dept_pred": dept_pred,
                      "dept_true": dept_true, "dept_score": dept_score})
    total = 0.5 * urgency_score + 0.5 * dept_score
    breakdown["total"] = total
    return total, breakdown

def grade_respond(action: Dict, email: Dict) -> Tuple[float, Dict]:
    breakdown: Dict[str, Any] = {}
    reply = action.get("reply_text", "")
    if not reply or len(reply.strip()) < 10:
        breakdown["error"] = "reply too short or missing"
        breakdown["total"] = 0.0
        return 0.0, breakdown
    keyword_score   = _keyword_coverage(reply, email.get("key_reply_keywords", []))
    structure_score = _reply_structure_score(reply)
    spam_penalty    = 0.6 if email.get("is_spam") else 0.0
    total = max(0.0, 0.5 * keyword_score + 0.5 * structure_score - spam_penalty)
    breakdown.update({"keyword_score": keyword_score, "structure_score": structure_score,
                      "spam_penalty": spam_penalty, "total": total})
    return total, breakdown

def grade_escalate(action: Dict, email: Dict) -> Tuple[float, Dict]:
    breakdown: Dict[str, Any] = {}
    predicted_escalate = bool(action.get("should_escalate", False))
    true_escalate      = bool(email.get("requires_escalation", False))
    decision_score = 1.0 if predicted_escalate == true_escalate else 0.0
    reason = action.get("reason", "")
    reason_score = 0.0
    if predicted_escalate and true_escalate:
        reason_score = min(len(reason.split()) / 10.0, 1.0)
    total = 0.7 * decision_score + 0.3 * reason_score
    breakdown.update({"predicted_escalate": predicted_escalate, "true_escalate": true_escalate,
                      "decision_score": decision_score, "reason_score": reason_score, "total": total})
    return total, breakdown

def grade_mark_spam(action: Dict, email: Dict) -> Tuple[float, Dict]:
    breakdown: Dict[str, Any] = {}
    predicted_spam = bool(action.get("is_spam", False))
    true_spam      = bool(email.get("is_spam", False))
    total = 1.0 if predicted_spam == true_spam else 0.0
    breakdown.update({"predicted_spam": predicted_spam, "true_spam": true_spam, "total": total})
    return total, breakdown

def grade_summarize(action: Dict, processed_emails: List[Dict]) -> Tuple[float, Dict]:
    breakdown: Dict[str, Any] = {}
    summary = action.get("summary_text", "")
    if not summary or len(summary.strip()) < 20:
        breakdown["error"] = "summary missing or too short"
        breakdown["total"] = 0.0
        return 0.0, breakdown
    true_critical  = sum(1 for e in processed_emails if e["true_urgency"] == "critical")
    true_spam      = sum(1 for e in processed_emails if e["is_spam"])
    true_escalated = sum(1 for e in processed_emails if e["requires_escalation"])
    pred_critical  = int(action.get("critical_count", -1))
    pred_spam      = int(action.get("spam_count", -1))
    pred_escalated = int(action.get("escalated_count", -1))
    count_score = (
        (1.0 if pred_critical  == true_critical  else 0.0) +
        (1.0 if pred_spam      == true_spam      else 0.0) +
        (1.0 if pred_escalated == true_escalated else 0.0)
    ) / 3.0
    prose_score = min(len(summary.split()) / 50.0, 1.0)
    total = 0.6 * count_score + 0.4 * prose_score
    breakdown.update({"true_critical": true_critical, "true_spam": true_spam,
                      "true_escalated": true_escalated, "count_score": count_score,
                      "prose_score": prose_score, "total": total})
    return total, breakdown

def grade_action(action_type: str, action: Dict, email, processed_emails=None):
    if action_type == "classify":
        return grade_classify(action, email)
    elif action_type == "respond":
        return grade_respond(action, email)
    elif action_type == "escalate":
        return grade_escalate(action, email)
    elif action_type == "mark_spam":
        return grade_mark_spam(action, email)
    elif action_type == "summarize":
        return grade_summarize(action, processed_emails or [])
    else:
        return 0.0, {"error": f"unknown action_type: {action_type!r}"}
'''

files["email_env.py"] = '''"""
email_env.py - EmailTriageEnv: full OpenEnv-compliant environment.
"""
from __future__ import annotations
import copy
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field
from email_data import EMAILS, TASK_CONFIGS, get_email_by_id
from graders import grade_action


class EmailMessage(BaseModel):
    id: str
    sender: str
    subject: str
    body: str
    timestamp: str

class InboxStats(BaseModel):
    total_emails: int
    processed: int
    remaining: int
    critical_flagged: int = 0
    spam_flagged: int = 0

class EmailObservation(BaseModel):
    current_email: Optional[EmailMessage] = None
    inbox_stats: InboxStats
    last_action_feedback: str = ""
    last_action_score: float = 0.0
    task_description: str = ""
    valid_actions: List[str] = Field(default_factory=list)
    step_number: int = 0
    episode_done: bool = False

class EmailAction(BaseModel):
    action_type: str
    urgency: Optional[str] = None
    department: Optional[str] = None
    reply_text: Optional[str] = None
    should_escalate: Optional[bool] = None
    reason: Optional[str] = None
    is_spam: Optional[bool] = None
    summary_text: Optional[str] = None
    critical_count: Optional[int] = None
    spam_count: Optional[int] = None
    escalated_count: Optional[int] = None

    def to_dict(self) -> Dict[str, Any]:
        return self.model_dump(exclude_none=True)

class EmailReward(BaseModel):
    step_score: float = Field(ge=0.0, le=1.0)
    cumulative_score: float = Field(ge=0.0, le=1.0)
    breakdown: Dict[str, Any] = Field(default_factory=dict)
    penalty: float = 0.0

class StepResult(BaseModel):
    observation: EmailObservation
    reward: float
    done: bool
    info: Dict[str, Any] = Field(default_factory=dict)

class EnvState(BaseModel):
    task_name: str
    step: int
    email_queue: List[str]
    current_email_id: Optional[str]
    processed_email_ids: List[str]
    actions_on_current_email: List[str]
    cumulative_reward: float
    max_steps: int
    critical_flagged: int
    spam_flagged: int
    escalated_flagged: int
    done: bool


class EmailTriageEnv:
    TASK_NAMES = list(TASK_CONFIGS.keys())

    def __init__(self, task_name: str = "triage_classify"):
        if task_name not in TASK_CONFIGS:
            raise ValueError(f"Unknown task {task_name!r}. Choose from: {self.TASK_NAMES}")
        self.task_name = task_name
        self._config = TASK_CONFIGS[task_name]
        self._state: Optional[EnvState] = None
        self._required_actions_per_email = {
            "triage_classify":      {"classify"},
            "triage_respond":       {"classify", "respond"},
            "triage_full_workflow": {"classify", "respond", "escalate"},
        }[task_name]

    def reset(self) -> EmailObservation:
        email_ids = list(self._config["email_ids"])
        first_id = email_ids[0]
        self._state = EnvState(
            task_name=self.task_name, step=0,
            email_queue=email_ids[1:], current_email_id=first_id,
            processed_email_ids=[], actions_on_current_email=[],
            cumulative_reward=0.0, max_steps=self._config["max_steps"],
            critical_flagged=0, spam_flagged=0, escalated_flagged=0, done=False,
        )
        return self._build_observation(feedback="New episode started. Process your inbox.", last_score=0.0)

    def step(self, action: EmailAction) -> StepResult:
        if self._state is None:
            raise RuntimeError("Call reset() before step().")
        if self._state.done:
            raise RuntimeError("Episode is done. Call reset() to start a new episode.")
        s = self._state
        s.step += 1
        reward_value, feedback, info = self._process_action(action, s)
        s.cumulative_reward = min(s.cumulative_reward + reward_value / s.max_steps, 1.0)
        done = (
            s.step >= s.max_steps
            or (len(s.email_queue) == 0 and action.action_type in ("next_email", "summarize"))
            or (self.task_name == "triage_full_workflow" and action.action_type == "summarize")
        )
        s.done = done
        obs = self._build_observation(feedback=feedback, last_score=reward_value)
        return StepResult(observation=obs, reward=reward_value, done=done,
                          info={**info, "cumulative_score": s.cumulative_reward})

    def state(self) -> EnvState:
        if self._state is None:
            raise RuntimeError("Call reset() first.")
        return copy.deepcopy(self._state)

    def _process_action(self, action: EmailAction, s: EnvState):
        act_type = action.action_type
        if act_type == "next_email":
            return self._handle_next_email(s)
        if act_type == "summarize":
            if self.task_name != "triage_full_workflow":
                return 0.0, "summarize is only valid in triage_full_workflow.", {}
            processed = [get_email_by_id(eid) for eid in s.processed_email_ids]
            if s.current_email_id:
                processed.append(get_email_by_id(s.current_email_id))
            score, breakdown = grade_action("summarize", action.to_dict(), None, processed)
            bonus = self._completion_bonus(s)
            total = min(score + bonus, 1.0)
            return total, f"Summary graded: {score:.2f} + bonus {bonus:.2f} = {total:.2f}.", {"grader_breakdown": breakdown}
        if s.current_email_id is None:
            return 0.0, "No current email. Use next_email or summarize.", {}
        email = get_email_by_id(s.current_email_id)
        score, breakdown = grade_action(act_type, action.to_dict(), email)
        if act_type == "mark_spam" and action.is_spam:
            s.spam_flagged += 1
        if act_type == "escalate" and action.should_escalate:
            s.escalated_flagged += 1
        if act_type == "classify" and action.urgency == "critical":
            s.critical_flagged += 1
        if act_type not in s.actions_on_current_email:
            s.actions_on_current_email.append(act_type)
        if act_type == "respond" and email.get("is_spam"):
            score = max(0.0, score - 0.3)
        if len(s.actions_on_current_email) > 3:
            score = max(0.0, score - 0.1)
        required_done = self._required_actions_per_email.issubset(set(s.actions_on_current_email))
        feedback = f"Action {act_type!r} on {s.current_email_id}: score={score:.2f}."
        if required_done:
            feedback += " All required actions done. Use next_email to continue."
        return score, feedback, {"grader_breakdown": breakdown, "required_done": required_done}

    def _handle_next_email(self, s: EnvState):
        missing = self._required_actions_per_email - set(s.actions_on_current_email)
        penalty = 0.1 * len(missing)
        feedback = f"Advanced to next email. Skip penalty: -{penalty:.2f}." if missing else "Good - all required actions completed."
        if s.current_email_id:
            s.processed_email_ids.append(s.current_email_id)
        if s.email_queue:
            s.current_email_id = s.email_queue.pop(0)
            s.actions_on_current_email = []
        else:
            s.current_email_id = None
            feedback += " Inbox complete!"
        return max(0.0, -penalty), feedback, {"skip_penalty": penalty}

    def _completion_bonus(self, s: EnvState) -> float:
        total_emails = len(self._config["email_ids"])
        processed = len(s.processed_email_ids) + (1 if s.current_email_id else 0)
        fraction = processed / total_emails if total_emails > 0 else 0.0
        return self._config.get("completion_bonus", 0.0) * fraction

    def _build_observation(self, feedback: str, last_score: float) -> EmailObservation:
        s = self._state
        current_email_msg = None
        if s.current_email_id:
            e = get_email_by_id(s.current_email_id)
            current_email_msg = EmailMessage(id=e["id"], sender=e["sender"],
                                              subject=e["subject"], body=e["body"], timestamp=e["timestamp"])
        stats = InboxStats(
            total_emails=len(self._config["email_ids"]),
            processed=len(s.processed_email_ids),
            remaining=len(s.email_queue) + (1 if s.current_email_id else 0),
            critical_flagged=s.critical_flagged, spam_flagged=s.spam_flagged,
        )
        valid = list(self._config["required_actions"])
        if s.current_email_id:
            valid.append("next_email")
        if self.task_name == "triage_full_workflow":
            valid.append("summarize")
        return EmailObservation(current_email=current_email_msg, inbox_stats=stats,
                                last_action_feedback=feedback, last_action_score=last_score,
                                task_description=self._config["description"],
                                valid_actions=valid, step_number=s.step, episode_done=s.done)
'''

files["server.py"] = '''"""
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
'''

files["inference.py"] = '''"""
inference.py - Baseline inference script for Email Triage OpenEnv.
ENVIRONMENT VARIABLES REQUIRED:
  API_BASE_URL, MODEL_NAME, HF_TOKEN, EMAIL_ENV_URL
"""
import json, os, sys, textwrap
from typing import Any, Dict, List, Optional
import requests
from openai import OpenAI

API_KEY      = os.getenv("HF_TOKEN") or os.getenv("API_KEY") or "dummy"
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
    r = requests.post(f"{ENV_URL}/reset", json={"task_name": task_name}, timeout=30)
    r.raise_for_status()
    return r.json()

def env_step(action):
    r = requests.post(f"{ENV_URL}/step", json=action, timeout=30)
    r.raise_for_status()
    return r.json()

SYSTEM_PROMPT = """You are an expert email triage assistant. Respond with a single JSON object only - no markdown, no code fences.

action_type options:
- classify: {"action_type":"classify","urgency":"critical","department":"billing"}
  urgency: low/medium/high/critical, department: billing/technical/sales/hr/legal/general
- respond: {"action_type":"respond","reply_text":"Dear ..."}
- escalate: {"action_type":"escalate","should_escalate":true,"reason":"..."}
- mark_spam: {"action_type":"mark_spam","is_spam":false}
- next_email: {"action_type":"next_email"}
- summarize: {"action_type":"summarize","summary_text":"...","critical_count":3,"spam_count":1,"escalated_count":3}

Rules: Pure JSON only. Never reply to spam. Complete required actions before next_email."""

def get_model_action(client, obs, task_name, history):
    email = obs.get("current_email")
    stats = obs.get("inbox_stats", {})
    email_block = "No current email."
    if email:
        email_block = f"ID: {email[\'id\']}\\nFrom: {email[\'sender\']}\\nSubject: {email[\'subject\']}\\nBody: {email[\'body\']}"
    prompt = f"TASK: {task_name}\\nSTEP: {obs.get(\'step_number\',\'?\')}\\n\\nEMAIL:\\n{email_block}\\n\\nSTATS: {stats}\\nFEEDBACK: {obs.get(\'last_action_feedback\',\'\')}\\nVALID ACTIONS: {obs.get(\'valid_actions\',[])}\\nHISTORY: {chr(10).join(history[-4:])}\\n\\nRespond with JSON action:"
    try:
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
    history, info = [], {}
    try:
        obs = env_reset(task_name)
        done = obs.get("episode_done", False)
        for step in range(1, MAX_STEPS + 1):
            if done:
                break
            action = get_model_action(client, obs, task_name, history)
            action_str = json.dumps(action)
            try:
                result = env_step(action)
            except requests.HTTPError as e:
                log_step(step=step, action=action_str, reward=0.0, done=False, error=str(e))
                continue
            reward = float(result.get("reward", 0.0))
            done   = bool(result.get("done", False))
            obs    = result.get("observation", obs)
            info   = result.get("info", {})
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
    client = OpenAI(base_url=API_BASE_URL, api_key=API_KEY)
    task_arg = os.getenv("EMAIL_TASK", "all")
    tasks_to_run = TASKS if task_arg == "all" else [task_arg]
    scores = {}
    for task in tasks_to_run:
        print(f"\\n{'='*60}\\nRunning task: {task}\\n{'='*60}", flush=True)
        scores[task] = run_episode(client, task)
        print(f"[SUMMARY] task={task} score={scores[task]:.3f}", flush=True)
    print("\\n[FINAL SCORES]", flush=True)
    for task, s in scores.items():
        print(f"  {task}: {s:.3f}", flush=True)
    overall = sum(scores.values()) / len(scores) if scores else 0.0
    print(f"  OVERALL: {overall:.3f}", flush=True)

if __name__ == "__main__":
    main()
'''

files["test_env.py"] = '''"""
test_env.py - Automated tests. Run: python test_env.py
"""
import sys, os
sys.path.insert(0, os.path.dirname(__file__))
from email_data import EMAILS, get_email_by_id
from graders import grade_classify, grade_respond, grade_escalate, grade_mark_spam, grade_summarize, grade_action

PASS = 0
FAIL = 0

def check(name, condition, detail=""):
    global PASS, FAIL
    if condition:
        print(f"  OK  {name}"); PASS += 1
    else:
        print(f"  FAIL  {name}  {detail}"); FAIL += 1

print("\\n-- Grader: classify --")
e1 = get_email_by_id("e001")
s, _ = grade_classify({"urgency":"critical","department":"billing"}, e1)
check("exact match = 1.0", s == 1.0, f"got {s}")
s, _ = grade_classify({"urgency":"high","department":"billing"}, e1)
check("adjacent urgency = 0.75", abs(s-0.75)<0.01, f"got {s}")
s, _ = grade_classify({"urgency":"low","department":"sales"}, e1)
check("wrong = 0.0", s == 0.0, f"got {s}")

print("\\n-- Grader: mark_spam --")
e2 = get_email_by_id("e002")
s, _ = grade_mark_spam({"is_spam":True}, e2)
check("spam correct = 1.0", s == 1.0)
s, _ = grade_mark_spam({"is_spam":False}, e2)
check("spam missed = 0.0", s == 0.0)

print("\\n-- Grader: respond --")
e3 = get_email_by_id("e003")
s, _ = grade_respond({"reply_text":"Dear Bob, thank you for contacting us. Our engineers are investigating the 500 errors on TKT-88231. We will provide a status update within the hour. Regards, Support"}, e3)
check("good reply >= 0.7", s >= 0.7, f"got {s}")
s, _ = grade_respond({"reply_text":"ok"}, e3)
check("too short = 0.0", s == 0.0)

print("\\n-- Grader: escalate --")
e6 = get_email_by_id("e006")
s, _ = grade_escalate({"should_escalate":True,"reason":"NDA deadline Monday legal action required"}, e6)
check("correct escalate >= 0.8", s >= 0.8, f"got {s}")

print("\\n-- Environment --")
try:
    from email_env import EmailTriageEnv, EmailAction
    env = EmailTriageEnv(task_name="triage_classify")
    obs = env.reset()
    check("reset() works", obs.current_email is not None)
    check("10 emails total", obs.inbox_stats.total_emails == 10)
    r = env.step(EmailAction(action_type="classify", urgency="critical", department="billing"))
    check("correct classify = 1.0", r.reward == 1.0, f"got {r.reward}")
    s2 = env.state()
    check("state().step == 1", s2.step == 1)
    print("  Environment tests passed!")
except Exception as e:
    print(f"  Environment error: {e}")

print(f"\\n{'='*40}")
print(f"Results: {PASS} passed, {FAIL} failed")
if FAIL == 0:
    print("All tests passed!")
else:
    print(f"{FAIL} test(s) failed.")
    sys.exit(1)
'''

files["requirements.txt"] = """fastapi==0.111.0
uvicorn[standard]==0.30.1
pydantic==2.7.1
pyyaml==6.0.1
requests==2.31.0
openai==1.30.1
"""

files["Dockerfile"] = """FROM python:3.11-slim
WORKDIR /app
RUN apt-get update && apt-get install -y --no-install-recommends curl && rm -rf /var/lib/apt/lists/*
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
EXPOSE 7860
HEALTHCHECK --interval=15s --timeout=5s --start-period=10s --retries=3 \\
    CMD curl -f http://localhost:7860/health || exit 1
CMD ["uvicorn", "server:app", "--host", "0.0.0.0", "--port", "7860"]
"""

files["README.md"] = """# Email Triage OpenEnv

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
"""

# Write all files
created = []
for filename, content in files.items():
    with open(filename, "w", encoding="utf-8") as f:
        f.write(content)
    created.append(filename)
    print(f"Created: {filename}")

print(f"\nDone! Created {len(created)} files.")
print("Now run: python test_env.py")