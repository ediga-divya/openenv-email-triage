"""
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
