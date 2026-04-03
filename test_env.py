"""
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

print("\n-- Grader: classify --")
e1 = get_email_by_id("e001")
s, _ = grade_classify({"urgency":"critical","department":"billing"}, e1)
check("exact match = 1.0", s == 1.0, f"got {s}")
s, _ = grade_classify({"urgency":"high","department":"billing"}, e1)
check("adjacent urgency = 0.75", abs(s-0.75)<0.01, f"got {s}")
s, _ = grade_classify({"urgency":"low","department":"sales"}, e1)
check("wrong = 0.0", s == 0.0, f"got {s}")

print("\n-- Grader: mark_spam --")
e2 = get_email_by_id("e002")
s, _ = grade_mark_spam({"is_spam":True}, e2)
check("spam correct = 1.0", s == 1.0)
s, _ = grade_mark_spam({"is_spam":False}, e2)
check("spam missed = 0.0", s == 0.0)

print("\n-- Grader: respond --")
e3 = get_email_by_id("e003")
s, _ = grade_respond({"reply_text":"Dear Bob, thank you for contacting us. Our engineers are investigating the 500 errors on TKT-88231. We will provide a status update within the hour. Regards, Support"}, e3)
check("good reply >= 0.7", s >= 0.7, f"got {s}")
s, _ = grade_respond({"reply_text":"ok"}, e3)
check("too short = 0.0", s == 0.0)

print("\n-- Grader: escalate --")
e6 = get_email_by_id("e006")
s, _ = grade_escalate({"should_escalate":True,"reason":"NDA deadline Monday legal action required"}, e6)
check("correct escalate >= 0.8", s >= 0.8, f"got {s}")

print("\n-- Environment --")
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

print(f"\n{'='*40}")
print(f"Results: {PASS} passed, {FAIL} failed")
if FAIL == 0:
    print("All tests passed!")
else:
    print(f"{FAIL} test(s) failed.")
    sys.exit(1)
