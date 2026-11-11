import streamlit as st
import pandas as pd
import time, datetime
from typing import List, Dict, Any

from services.analyzer import get_analyzer
from services.db import init_db, insert_user_record, fetch_user_data, fetch_user_full
from data.courses import ds_course, web_course, android_course, ios_course, uiux_course, get_resume_videos, get_interview_videos
from streamlit_tags import st_tags
import plotly.express as px

st.set_page_config(page_title="AI Resume Analyzer", page_icon="🧠", layout="wide", initial_sidebar_state="expanded")
init_db()

st.markdown("""
<div style="background: linear-gradient(135deg, #0ea5e9 0%, #6366f1 60%, #9333ea 100%);
            color: white; padding: 16px 20px; border-radius: 14px; margin-bottom: 12px;">
  <h2 style="margin:0;">AI Resume Analyzer — Python + NLP</h2>
  <p style="margin:4px 0 0 0; opacity:0.95;">Parse, score, and match resumes to JDs, with recommendations and admin dashboard.</p>
</div>
""", unsafe_allow_html=True)

with st.sidebar:
    st.header("Mode")
    mode = st.radio("Choose", ["User", "Admin"], horizontal=True)
    st.divider()
    st.caption("Tip: Admin shows saved analyses and charts.")

# ---------------- User Mode ----------------
if mode == "User":
    col_left, col_right = st.columns([1.1, 0.9], gap="large")
    with col_left:
        st.subheader("Job Description")
        jd_text = st.text_area("Paste the JD here", height=220, placeholder="Responsibilities…\nRequired Skills: Python, NLP…")
    with col_right:
        st.subheader("Upload Resumes (PDF, DOCX, TXT)")
        files = st.file_uploader("Drag & drop or browse", type=["pdf","docx","txt"], accept_multiple_files=True)

    with st.expander("Weights (optional)"):
        c1,c2,c3,c4 = st.columns(4)
        with c1: w_skill = st.slider("Skill", 0, 100, 45, step=5)
        with c2: w_sem   = st.slider("Semantic", 0, 100, 25, step=5)
        with c3: w_kw    = st.slider("Keyword", 0, 100, 20, step=5)
        with c4: w_exp   = st.slider("Experience", 0, 100, 10, step=5)

    analyze_disabled = not (jd_text.strip() and files)
    if st.button("🔎 Analyze", type="primary", disabled=analyze_disabled):
        analyzer = get_analyzer()
        results: List[Dict[str, Any]] = []
        prog = st.progress(0.0, text="Analyzing resumes…")

        for i, f in enumerate(files, start=1):
            try:
                r = analyzer.analyze_resume_file(
                    f, jd_text,
                    weights={"skill": w_skill, "semantic": w_sem, "keyword": w_kw, "exp": w_exp},
                )
                results.append(r)
            except Exception as e:
                st.error(f"Failed to analyze {f.name}: {e}")
            prog.progress(i/len(files), text=f"Analyzed {i}/{len(files)}")

        if results:
            st.session_state["results"] = results

    results = st.session_state.get("results", [])
    if results:
        st.success("Analysis complete ✅")
        df = pd.DataFrame([{
            "File": r["file_name"],
            "Pages": r.get("page_no", 1),
            "Candidate": r["candidate"].get("name", ""),
            "Email": r["candidate"].get("email", ""),
            "Phone": r["candidate"].get("phone", ""),
            "TotalExpMonths": r["candidate"].get("total_experience_months", 0),
            "OverallScore": round(r["scores"]["overall"], 2),
            "SkillMatch": round(r["scores"]["skill_match"], 2),
            "SemanticSim": round(r["scores"]["semantic_similarity"], 2),
            "KeywordCoverage": round(r["scores"]["keyword_coverage"], 2),
            "ResumeScore": r.get("resume_score", 0),
            "PredictedField": r.get("predicted_field", ""),
            "UserLevel": r.get("user_level", ""),
        } for r in results]).sort_values(by="OverallScore", ascending=False)

        st.dataframe(df, use_container_width=True, height=360)

        for r in results:
            field = r.get("predicted_field", "Data Science")
            missing_skills = r["explanations"].get("missing_skills", [])
            rec_courses = ds_course if field=="Data Science" else web_course if field=="Web Development" else android_course if field=="Android Development" else ios_course if field=="IOS Development" else uiux_course

            ts = time.time()
            cur_date = datetime.datetime.fromtimestamp(ts).strftime('%Y-%m-%d')
            cur_time = datetime.datetime.fromtimestamp(ts).strftime('%H:%M:%S')
            timestamp = f"{cur_date}_{cur_time}"

            insert_user_record({
                "name": r["candidate"].get("name",""),
                "email": r["candidate"].get("email",""),
                "resume_score": r.get("resume_score",0),
                "timestamp": timestamp,
                "page_no": str(r.get("page_no",1)),
                "predicted_field": field,
                "user_level": r.get("user_level",""),
                "actual_skills": ", ".join(r["skills"]["resume_skills"]),
                "recommended_skills": ", ".join(missing_skills),
                "recommended_courses": ", ".join([c[0] for c in rec_courses[:3]]),
            })

            with st.expander(f"📄 {r['file_name']} — Overall {r['scores']['overall']:.2f} | ResumeScore {r.get('resume_score',0)} | {field} • {r.get('user_level','')}"):
                c = r["candidate"]
                st.markdown(f"**Candidate:** {c.get('name','(unknown)')}")
                st.markdown(f"**Email:** {c.get('email','-')}")
                st.markdown(f"**Phone:** {c.get('phone','-')}")
                st.markdown(f"**Pages:** {r.get('page_no',1)}")
                st.markdown(f"**Experience (months):** {c.get('total_experience_months',0)}")

                st.markdown("**Resume Score Notes:**")
                for n in r.get("score_notes", []):
                    st.write(f"- {n}")

                ms = r["explanations"]["matched_skills"]
                miss = r["explanations"]["missing_skills"]
                st.markdown("**Matched skills:** " + (", ".join(sorted(ms)) if ms else "-"))
                st.markdown("**Missing JD skills:** " + (", ".join(sorted(miss)) if miss else "-"))

                st.markdown("**Your skills (editable):**")
                st_tags(label="Skills that you have", text="Edit or add missing skills", value=r["skills"]["resume_skills"], key=f"tags-{r['file_name']}")

                st.markdown("**Recommended courses:**")
                for title, link in rec_courses[:3]:
                    st.markdown(f"- [{title}]({link})")

                # ✅ Updated label here
                st.markdown("**Helpful videos:**")
                for url in get_resume_videos(field, miss):
                    st.markdown(f"[![YouTube](https://img.icons8.com/color/48/000000/youtube-play.png)]({url}) Click to watch")

                st.markdown("**Helpful interview videos:**")
                for url in get_interview_videos(field):
                    st.markdown(f"[![YouTube](https://img.icons8.com/color/48/000000/youtube-play.png)]({url}) Click to watch")

        csv = df.to_csv(index=False).encode("utf-8")
        st.download_button("⬇️ Download CSV", data=csv, file_name="resume_analysis.csv", mime="text/csv", use_container_width=True)

# ---------------- Admin Mode ----------------
if mode == "Admin":
    st.subheader("Saved analyses")
    rows = fetch_user_data()
    if not rows:
        st.info("No saved data yet. Run some analyses in User mode.")
    else:
        cols = ["ID","Name","Email","ResumeScore","Timestamp","Pages","PredictedField","Level"]
        df = pd.DataFrame(rows, columns=cols)
        st.dataframe(df, use_container_width=True, height=380)

        st.markdown("### 📊 Distribution")
        colA, colB = st.columns(2)
        with colA:
            fig = px.histogram(df, x="PredictedField", title="Predicted Field")
            st.plotly_chart(fig, use_container_width=True)
        with colB:
            fig2 = px.histogram(df, x="Level", title="User Level")
            st.plotly_chart(fig2, use_container_width=True)

        st.markdown("### 🔎 Inspect a record")
        sel = st.selectbox("Pick ID", df["ID"])
        full = fetch_user_full(int(sel))
        if full:
            _, name, email, resume_score, ts, pages, field, level, actual_skills, rec_skills, rec_courses = full
            st.write(f"**Name:** {name}")
            st.write(f"**Email:** {email}")
            st.write(f"**Resume Score:** {resume_score}")
            st.write(f"**Timestamp:** {ts}")
            st.write(f"**Pages:** {pages}")
            st.write(f"**Field:** {field}")
            st.write(f"**Level:** {level}")
            st.write(f"**Skills:** {actual_skills}")
            st.write(f"**Recommended Skills:** {rec_skills}")
            st.write(f"**Recommended Courses:** {rec_courses}")
