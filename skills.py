from typing import Dict, List, Set
import re

def load_skill_lexicon() -> Dict[str, List[str]]:
    return {
        "python": ["py"],
        "java": [],
        "javascript": ["js", "ecmascript"],
        "typescript": ["ts"],
        "react": ["reactjs", "react.js"],
        "node.js": ["node", "nodejs"],
        "django": [],
        "flask": [],
        "fastapi": [],
        "sql": [],
        "mysql": [],
        "mongodb": ["mongo"],
        "redis": [],
        "aws": ["amazon web services", "ec2", "s3", "lambda"],
        "gcp": ["google cloud"],
        "azure": [],
        "docker": [],
        "kubernetes": ["k8s"],
        "linux": [],
        "git": [],
        "nlp": ["natural language processing"],
        "machine learning": ["ml"],
        "deep learning": ["dl"],
        "pytorch": [],
        "tensorflow": [],
        "sklearn": ["scikit-learn"],
        "pandas": [],
        "numpy": [],
        "opencv": [],
        "html": [],
        "css": [],
        "rest api": ["rest", "restful"],
        "graphql": [],
        "ci/cd": ["cicd", "continuous integration", "continuous delivery"],
        "microservices": [],
        "tableau": [],
        "power bi": ["powerbi"],
    }

def _compile_patterns(lex: Dict[str, List[str]]):
    pats = []
    for skill, aliases in lex.items():
        words = [skill] + aliases
        words = [re.escape(w) for w in words]
        pat = r"\b(" + "|".join(words) + r")\b"
        pats.append((skill, re.compile(pat, re.IGNORECASE)))
    return pats

def extract_skills(text: str, lex: Dict[str, List[str]]) -> Set[str]:
    pats = _compile_patterns(lex)
    found = set()
    for base, rx in pats:
        if rx.search(text):
            found.add(base)
    return found

def normalize_skills(skills: Set[str]) -> Set[str]:
    return set(s.lower().strip() for s in skills)
