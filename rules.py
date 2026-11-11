from typing import Tuple, List
from pdfminer.high_level import extract_pages

FIELD_KEYWORDS = {
    "Data Science": ["python", "pandas", "numpy", "machine learning", "deep learning", "tensorflow", "pytorch", "nlp"],
    "Web Development": ["react", "django", "flask", "javascript", "node.js", "html", "css"],
    "Android Development": ["android", "kotlin", "java", "xml", "android studio"],
    "IOS Development": ["ios", "swift", "xcode", "cocoa"],
    "UI-UX": ["ui/ux", "figma", "sketch", "adobe xd", "wireframe", "prototype"],
}

def compute_resume_score(resume_text: str) -> Tuple[int, List[str]]:
    score = 0
    notes = []
    text_low = resume_text.lower()

    checks = [
        ("objective/summary", any(h in text_low for h in ["objective", "summary"])),
        ("education", "education" in text_low),
        ("experience", "experience" in text_low or "work experience" in text_low),
        ("projects", "project" in text_low or "projects" in text_low),
        ("skills", "skills" in text_low),
    ]
    for label, ok in checks:
        if ok:
            score += 20
            notes.append(f"[+] {label} present")
        else:
            notes.append(f"[-] {label} missing")

    return min(score, 100), notes

def predict_field_and_level(resume_text: str, skills: set, total_exp_months: int) -> Tuple[str, str]:
    text_low = resume_text.lower()
    field_scores = {k: 0 for k in FIELD_KEYWORDS}
    for field, kws in FIELD_KEYWORDS.items():
        for kw in kws:
            if kw in text_low or kw in skills:
                field_scores[field] += 1
    predicted_field = max(field_scores, key=field_scores.get)

    if total_exp_months >= 60:
        level = "Experienced"
    elif total_exp_months >= 24:
        level = "Intermediate"
    else:
        level = "Fresher"

    return predicted_field, level

def extract_page_count(file_like) -> int:
    if file_like.name.lower().endswith(".pdf"):
        total = 0
        for _ in extract_pages(file_like):
            total += 1
        file_like.seek(0)
        return max(total, 1)
    return 1
