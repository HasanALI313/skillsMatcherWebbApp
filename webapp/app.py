import sys, os

os.environ.setdefault("ADZUNA_APP_ID", "9109bf5d")
os.environ.setdefault("ADZUNA_API_KEY", "449dd455947b555dd8910a08a9fc5f8f")
os.environ.setdefault("ADZUNA_COUNTRY", "gb")
os.environ.setdefault("GEMINI_API_KEY", "AQ.Ab8RN6Io0Zc_oFIOouQisQbz5wXd-__Lwjovo1lpGzwovUsW6Q")
os.environ.setdefault("GEMINI_MODEL", "gemini-3.1-flash-lite-preview")

sys.path.insert(0, os.path.dirname(__file__))

try:
    from webapp.adzuna import search_jobs
    from webapp.llm_matcher import match_top_3, get_job_skills
except ImportError:
    from adzuna import search_jobs
    from llm_matcher import match_top_3, get_job_skills

from flask import Flask, render_template, request, session
from datetime import datetime

app = Flask(__name__)
app.secret_key = os.urandom(24).hex()

import sys as _sys
_sys.stderr.write("[startup] Checking environment variables...\n")
_env_names = [
    "GEMINI_API_KEY", "GEMINI_MODEL",
    "ADZUNA_APP_ID", "ADZUNA_API_KEY", "ADZUNA_COUNTRY",
]
for _name in _env_names:
    _sys.stderr.write("[startup]   {}: {}\n".format(
        _name, "SET" if os.environ.get(_name) else "NOT SET"
    ))
_sys.stderr.write("[startup] All env var names in environment: {}\n".format(
    [k for k in os.environ.keys() if "KEY" in k.upper() or "API" in k.upper() or "GEMINI" in k.upper() or "ADZUNA" in k.upper()]
))
_sys.stderr.flush()

@app.route("/")
def home():
    return render_template("home.html", active="home", now=datetime.now())

@app.route("/health")
def health():
    matching_vars = [
        k for k in os.environ.keys()
        if any(x in k.upper() for x in ["GEMINI", "ADZUNA", "API_KEY", "APP_ID"])
    ]
    return {
        "status": "ok",
        "gemini_key_set": bool(os.environ.get("GEMINI_API_KEY")),
        "gemini_model": os.environ.get("GEMINI_MODEL") or "default",
        "adzuna_id_set": bool(os.environ.get("ADZUNA_APP_ID")),
        "adzuna_key_set": bool(os.environ.get("ADZUNA_API_KEY")),
        "matching_env_var_names_found": matching_vars,
        "config_py_exists": os.path.isfile(os.path.join(os.path.dirname(__file__), "config.py")),
    }

@app.route("/find")
def find():
    return render_template("find_job.html", active="find", now=datetime.now())

@app.route("/match", methods=["POST"])
def match():
    user_skills = [request.form.get(f"skill{i}") for i in range(1, 6)]
    user_skills = [s.strip() for s in user_skills if s and s.strip()]
    if not user_skills:
        return render_template("find_job.html", active="find", now=datetime.now(), error="Please enter at least one skill.")
    try:
        top_3 = match_top_3(user_skills)
        session["last_match"] = [(title, skills) for title, score, skills in top_3]
        return render_template("find_job.html", active="find", now=datetime.now(), top_3=top_3, user_skills=user_skills)
    except RuntimeError as e:
        return render_template("find_job.html", active="find", now=datetime.now(), error=str(e))

@app.route("/build/<path:job_title>")
def build(job_title):
    required = None
    if "last_match" in session:
        for title, skills in session["last_match"]:
            if title == job_title:
                required = skills
                break
    if not required:
        required = get_job_skills(job_title)
    return render_template("build.html", active="find", job_title=job_title, required=required, now=datetime.now())

@app.route("/generate", methods=["POST"])
def generate():
    data = request.form
    job_title = data.get("job_title")
    required = None
    if "last_match" in session:
        for title, skills in session["last_match"]:
            if title == job_title:
                required = skills
                break
    if not required:
        required = get_job_skills(job_title)
    return render_template("generated.html", active="find", data=data, required=required or [], now=datetime.now())

@app.route("/jobs")
def jobs_list():
    job_title = request.args.get("q", "")
    if not job_title:
        return render_template("jobs.html", active="find", now=datetime.now(), query="", listings=[])
    listings = search_jobs(job_title)
    return render_template("jobs.html", active="find", now=datetime.now(), query=job_title, listings=listings, can_build=True)

@app.route("/contact", methods=["GET", "POST"])
def contact():
    if request.method == "POST":
        return render_template("contact.html", active="contact", now=datetime.now(), success="Thanks for reaching out! We'll get back to you soon.")
    return render_template("contact.html", active="contact", now=datetime.now())

if __name__ == "__main__":
    app.run(debug=True)
