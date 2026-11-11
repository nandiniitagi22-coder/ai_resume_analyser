from typing import Dict, Any, List
from dataclasses import dataclass

from nlp.parser import extract_text_from_filelike, extract_contacts, estimate_total_experience_months, sentencize
from utils.rules import compute_resume_score, predict_field_and_level, extract_page_count

@dataclass
class Analyzer:
    nlp: any
    sbert_model: any
    jd_skill_lexicon: Dict[str, List[str]]

    def analyze_resume_file(self, file_like, jd_text: str, weights: Dict[str,int]) -> Dict[str, Any]:
        text = extract_text_from_filelike(file_like)
        page_no = extract_page_count(file_like)
        return self.analyze_text(text, file_like.name, page_no, jd_text, weights)

    def analyze_text(self, resume_text: str, file_name: str, page_no: int, jd_text: str, weights: Dict[str,int]) -> Dict[str, Any]:
        from nlp.skills import load_skill_lexicon, extract_skills, normalize_skills
        from nlp.scoring import compute_scores

        contacts = extract_contacts(self.nlp, resume_text)
        total_exp = estimate_total_experience_months(resume_text)

        lex = self.jd_skill_lexicon or load_skill_lexicon()
        resume_skills = normalize_skills(extract_skills(resume_text, lex))
        jd_skills = normalize_skills(extract_skills(jd_text, lex))

        scores, explanations = compute_scores(
            resume_text=resume_text,
            jd_text=jd_text,
            resume_skills=resume_skills,
            jd_skills=jd_skills,
            nlp=self.nlp,
            sbert_model=self.sbert_model,
            weights=weights,
        )

        resume_score, score_notes = compute_resume_score(resume_text)
        predicted_field, user_level = predict_field_and_level(resume_text, resume_skills, total_exp)

        evidence = []
        matched = explanations.get("matched_skills", [])
        if matched:
            sents = [s.text.strip() for s in sentencize(self.nlp, resume_text)]
            for kw in matched:
                for s in sents:
                    if kw.lower() in s.lower() and s not in evidence:
                        evidence.append(s)
                        if len(evidence) >= 12:
                            break
                if len(evidence) >= 12:
                    break

        return {
            "file_name": file_name,
            "page_no": page_no,
            "candidate": {
                "name": contacts.get("name",""),
                "email": contacts.get("email",""),
                "phone": contacts.get("phone",""),
                "total_experience_months": total_exp,
            },
            "skills": {
                "resume_skills": sorted(list(resume_skills)),
                "jd_skills": sorted(list(jd_skills)),
            },
            "scores": scores,
            "resume_score": resume_score,
            "score_notes": score_notes,
            "predicted_field": predicted_field,
            "user_level": user_level,
            "explanations": {**explanations, "evidence": evidence},
        }

_cached = {"analyzer": None}

def get_analyzer() -> Analyzer:
    if _cached["analyzer"] is not None:
        return _cached["analyzer"]

    import spacy
    from sentence_transformers import SentenceTransformer
    from nlp.skills import load_skill_lexicon

    nlp = spacy.load("en_core_web_sm")
    sbert_model = SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2")
    lexicon = load_skill_lexicon()

    _cached["analyzer"] = Analyzer(nlp=nlp, sbert_model=sbert_model, jd_skill_lexicon=lexicon)
    return _cached["analyzer"]
