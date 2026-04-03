"""
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
    if re.search(r"\b(hi|hello|dear|good (morning|afternoon|evening))\b", reply, re.I):
        score += 0.25
    word_count = len(reply.split())
    if word_count >= 30:
        score += 0.40
    elif word_count >= 15:
        score += 0.20
    if re.search(r"\b(regards|sincerely|thank(s| you)|best|cheers)\b", reply, re.I):
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
