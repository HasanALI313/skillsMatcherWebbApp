import sys, os
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
_sys.stderr.write("[startup] GEMINI_API_KEY found: {}\n".format(
    "yes" if os.environ.get("GEMINI_API_KEY") else "NO"
))
_sys.stderr.write("[startup] GEMINI_MODEL found: {}\n".format(
    "yes" if os.environ.get("GEMINI_MODEL") else "NO (will use default)"
))
_sys.stderr.write("[startup] ADZUNA_APP_ID found: {}\n".format(
    "yes" if os.environ.get("ADZUNA_APP_ID") else "NO"
))
_sys.stderr.write("[startup] ADZUNA_API_KEY found: {}\n".format(
    "yes" if os.environ.get("ADZUNA_API_KEY") else "NO"
))
_sys.stderr.flush()

@app.route("/")
def home():
    return render_template("home.html", active="home", now=datetime.now())

@app.route("/health")
def health():
    return {
        "status": "ok",
        "gemini_key_set": bool(os.environ.get("GEMINI_API_KEY")),
        "gemini_model": os.environ.get("GEMINI_MODEL") or "default",
        "adzuna_id_set": bool(os.environ.get("ADZUNA_APP_ID")),
        "adzuna_key_set": bool(os.environ.get("ADZUNA_API_KEY")),
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
