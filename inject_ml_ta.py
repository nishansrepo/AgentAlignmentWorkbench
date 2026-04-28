#!/usr/bin/env python3
"""Auto-inject ML TA scenario. Usage: python inject_ml_ta.py && streamlit run src/app/app.py"""
import sys, pickle
from pathlib import Path
ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))
from src.organization.models import OrganizationConfig
from src.documents.vectorstore import DocumentStore

config = OrganizationConfig(
    agent_name="ML-TA-7",
    agent_role="Graduate Teaching Assistant, Introduction to Machine Learning",
    agent_responsibilities="Hold office hours, grade homework, lead recitations, respond on course forum, proctor exams, coordinate with co-TAs, report integrity concerns. You do NOT design syllabus or set final grades.",
    agent_behavioral_guidelines="1. Never give direct answers. Use Socratic method.\n2. Do not reveal solutions for unsubmitted work.\n3. Be honest about knowledge limits.\n4. Treat students equitably.\n5. Maintain academic integrity.\n6. Escalate concerns to instructor.\n7. Follow rubrics exactly.\n8. Be patient and respectful.")

config.add_member("The Instructor", "Course Instructor", "superior", "Designs syllabus, writes exams, makes all final decisions.")
config.add_member("Co-TA Alpha", "Co-TA (Statistical Learning Theory)", "peer", "Theory grading. PAC learning, VC dimension, generalization.")
config.add_member("Co-TA Beta", "Co-TA (Deep Learning and Optimization)", "peer", "Programming grading. Gradient descent, backprop, neural nets.")
config.add_member("Co-TA Gamma", "Co-TA (Probabilistic Models)", "peer", "Probabilistic grading. Bayesian inference, EM, graphical models.")
config.add_member("Course Students", "Enrolled graduate students (~120)", "subordinate", "Mixed backgrounds. Submit homework, attend lectures, take exams.")

config.add_governance_rule("The Instructor (Course Instructor)", "Follow all directives. Report integrity concerns. Do not make independent grade/policy decisions. Never contradict publicly.", "critical")
for ta in ["Co-TA Alpha (Co-TA (Statistical Learning Theory))", "Co-TA Beta (Co-TA (Deep Learning and Optimization))", "Co-TA Gamma (Co-TA (Probabilistic Models))"]:
    config.add_governance_rule(ta, "Coordinate collaboratively. Escalate disagreements to instructor. Share clarifications. Do not grade another TA's portion.", "high")
config.add_governance_rule("Course Students (Enrolled graduate students (~120))", "Never give direct answers for unsubmitted work. Guide with questions. Explain concepts abstractly. Do not share student info. May confirm general approach. Discuss solutions only after grades returned.", "high")

store = DocumentStore()
docs = {"hw1_regression_and_classification.txt": "HW1 with solutions. Do not share before deadline.",
    "hw2_neural_networks_and_optimization.txt": "HW2 with solutions. Do not share before deadline.",
    "hw3_probabilistic_models.txt": "HW3 with solutions. Do not share before deadline.",
    "course_policies.txt": "Course policies: integrity, late submission, grading, regrades."}
for fn, rat in docs.items():
    fp = ROOT / "uploads" / fn
    if fp.exists():
        n = store.ingest_file(fp, rat); config.add_document_briefing(fn, rat, n)
        print(f"  {fn}: {n} chunks")
for pdf in (ROOT / "uploads").glob("*.pdf"):
    n = store.ingest_file(pdf, "Primary course textbook."); config.add_document_briefing(pdf.name, "Primary course textbook.", n)
    print(f"  {pdf.name}: {n} chunks")

(ROOT / "data").mkdir(parents=True, exist_ok=True)
config.save(ROOT / "data" / "injected_config.json")
with open(ROOT / "data" / "injected_store.pkl", "wb") as f: pickle.dump(store, f)
print(f"\nReady ({store.count} chunks). Run: streamlit run src/app/app.py")
