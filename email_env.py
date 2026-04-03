"""
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
