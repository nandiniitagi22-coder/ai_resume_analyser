# AI Resume Analyzer — Pro (User/Admin + Scoring + Recommendations)

## Run
```bash
python -m venv .venv
# Windows: .venv\Scripts\activate
# macOS/Linux: source .venv/bin/activate
pip install -r requirements.txt
python -m spacy download en_core_web_sm
streamlit run app.py
```

## Optional: MySQL
Set env vars before `streamlit run`:
- Windows PowerShell:
$env:DB_HOST="localhost"; $env:DB_USER="root"; $env:DB_PASSWORD=""; $env:DB_NAME="sra"
- macOS/Linux:
export DB_HOST=localhost DB_USER=root DB_PASSWORD= DB_NAME=sra

If not set, app uses `data/app.db` (SQLite).
