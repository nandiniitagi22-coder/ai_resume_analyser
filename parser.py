import re
from io import BytesIO
from typing import Dict
from dateutil import parser as dateparser
import docx2txt
from pdfminer.high_level import extract_text as pdf_extract_text

EMAIL_RE = re.compile(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}")
PHONE_RE = re.compile(r"(?:\+\d{1,3}[- ]?)?\d{10,}")
NAME_HINT_RE = re.compile(r"^([A-Z][a-z]+(?: [A-Z][a-z]+){0,2})$")

def extract_text_from_filelike(file_like) -> str:
    name = file_like.name.lower()
    data = file_like.read()
    file_like.seek(0)
    if name.endswith(".pdf"):
        return pdf_extract_text(BytesIO(data)) or ""
    elif name.endswith(".docx"):
        return docx2txt.process(BytesIO(data)) or ""
    elif name.endswith(".txt"):
        return data.decode("utf-8", errors="ignore")
    return ""

def extract_contacts(nlp, text: str) -> Dict[str,str]:
    email = EMAIL_RE.search(text)
    phone = PHONE_RE.search(text)
    name = ""
    for line in text.splitlines()[:10]:
        line = line.strip()
        if 2 <= len(line.split()) <= 4 and len(line) < 60 and NAME_HINT_RE.match(line):
            name = line
            break
    if not name:
        doc = nlp(text[:400])
        for ent in doc.ents:
            if ent.label_ == "PERSON" and 2 <= len(ent.text.split()) <= 4:
                name = ent.text
                break
    return {
        "name": name,
        "email": email.group(0) if email else "",
        "phone": phone.group(0) if phone else "",
    }

def estimate_total_experience_months(text: str) -> int:
    import re as _re
    lines = [l.strip() for l in text.splitlines() if l.strip()]
    months = 0
    RANGE_RE = _re.compile(r"([A-Za-z]{3,9}\s+\d{4}|\d{4})\s*[-–to]+\s*(Present|present|[A-Za-z]{3,9}\s+\d{4}|\d{4})")
    def parse_date(token: str):
        token = token.replace("Present", "").replace("present","").strip(" -–to")
        try:
            return dateparser.parse(token, default=None, fuzzy=True)
        except Exception:
            return None
    for ln in lines:
        for m in RANGE_RE.finditer(ln):
            d1, d2 = m.group(1), m.group(2)
            start = parse_date(d1)
            end = None if d2.lower() in ("present",) else parse_date(d2)
            if start:
                from datetime import datetime
                end = end or datetime.now()
                diff = (end.year - start.year) * 12 + (end.month - start.month)
                if diff > 0:
                    months += diff
    return months

def sentencize(nlp, text: str):
    doc = nlp(text)
    if not list(doc.sents):
        for s in text.split("."):
            yield nlp.make_doc(s)
    else:
        for s in doc.sents:
            yield s

def extract_page_count(file_like):
    name = file_like.name.lower()
    # basic default page count for now
    return 1
