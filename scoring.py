from typing import Dict, Any, Set
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

def _normalize_weights(w: Dict[str,int]) -> Dict[str,float]:
    total = sum(w.values()) if w else 100
    if total == 0:
        return {k: 0.0 for k in w}
    return {k: (v/total) for k,v in w.items()}

def compute_scores(resume_text: str, jd_text: str, resume_skills: Set[str], jd_skills: Set[str], nlp, sbert_model, weights: Dict[str,int]):
    w = _normalize_weights(weights or {"skill":45, "semantic":25, "keyword":20, "exp":10})

    inter = resume_skills.intersection(jd_skills)
    matched_skills = sorted(list(inter))
    missing_skills = sorted(list(jd_skills - resume_skills))
    skill_match = 100.0 * (len(inter) / max(1, len(jd_skills)))

    embs = sbert_model.encode([jd_text, resume_text], normalize_embeddings=True)
    semantic_sim = float(cosine_similarity([embs[0]], [embs[1]])[0][0] * 100.0)

    vec = TfidfVectorizer(stop_words='english', ngram_range=(1,2), min_df=1)
    tf = vec.fit_transform([jd_text, resume_text])
    kw_cov = float(cosine_similarity(tf[0], tf[1])[0][0] * 100.0)

    exp_score = 0.0

    overall = (w.get("skill",0)*skill_match +
               w.get("semantic",0)*semantic_sim +
               w.get("keyword",0)*kw_cov +
               w.get("exp",0)*exp_score)

    return ({
        "skill_match": skill_match,
        "semantic_similarity": semantic_sim,
        "keyword_coverage": kw_cov,
        "experience": exp_score,
        "overall": overall
    }, {
        "matched_skills": matched_skills,
        "missing_skills": missing_skills
    })
