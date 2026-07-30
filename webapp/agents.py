import os
import json
from google import genai

try:
    from webapp.config import GEMINI_API_KEY, GEMINI_MODEL
except ImportError:
    try:
        from config import GEMINI_API_KEY, GEMINI_MODEL
    except ImportError:
        GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY", "")
        GEMINI_MODEL = os.environ.get("GEMINI_MODEL", "gemini-2.0-flash-lite")

_client = None
_model = GEMINI_MODEL


def _get_client():
    global _client
    if _client is None:
        if not GEMINI_API_KEY:
            raise RuntimeError(
                "GEMINI_API_KEY is not set. "
                "Set it as an environment variable."
            )
        _client = genai.Client(api_key=GEMINI_API_KEY)
    return _client


def _call_llm(prompt, response_schema=None):
    client = _get_client()
    resp = client.models.generate_content(model=_model, contents=prompt)
    raw = resp.text.strip()
    raw = raw.removeprefix("```json").removeprefix("```").removesuffix("```").strip()
    if response_schema:
        return json.loads(raw)
    return raw


class SkillMatcherAgent:
    def match(self, skills):
        prompt = f"""Given these skills: {", ".join(skills)}

Suggest the top 3 job titles that best match these skills.
For each job title, list exactly 10 key skills required for that role.

Return ONLY valid JSON in this exact format (no markdown, no code fences, no extra text):
[{{"title": "Job Title", "skills": ["skill1", "skill2", ...]}}, ...]"""
        data = _call_llm(prompt, response_schema=True)
        results = []
        for entry in data[:3]:
            title = entry["title"]
            required = entry["skills"][:10]
            score = len(set(s.lower() for s in skills) & set(s.lower() for s in required))
            results.append((title, score, required))
        return results

    def get_skills_for_title(self, title):
        prompt = f"""List exactly 10 key skills required for the role: {title}

Return ONLY valid JSON in this exact format (no markdown, no code fences, no extra text):
{{"skills": ["skill1", "skill2", "skill3", "skill4", "skill5", "skill6", "skill7", "skill8", "skill9", "skill10"]}}"""
        try:
            data = _call_llm(prompt, response_schema=True)
            return data["skills"][:10]
        except Exception:
            return []


class CvBuilderAgent:
    def build(self, user_data, job_title, required_skills):
        prompt = f"""You are a professional CV writer. Create a tailored CV for a {job_title} position.

User details:
- Name: {user_data.get('name', '')}
- Email: {user_data.get('email', '')}
- Phone: {user_data.get('phone', '')}
- Location: {user_data.get('location', '')}
- Professional Summary: {user_data.get('summary', '')}
- Work Experience: {user_data.get('experience', '')}
- Education: {user_data.get('education', '')}
- Key Achievements: {user_data.get('achievements', '')}

Key skills required for this role: {", ".join(required_skills)}

Generate a professional CV in plain text format. Include sections for:
1. Name and contact info
2. Professional Summary (rewrite the user's summary to be more compelling for this role)
3. Key Skills (incorporate the required skills naturally)
4. Work Experience (expand the user's experience with bullet points relevant to this role)
5. Education
6. Key Achievements (formatted as impactful bullet points)

Make it concise, impactful, and tailored to the {job_title} role. Use professional language.

Return ONLY the CV text, no markdown fences, no extra commentary."""
        return _call_llm(prompt)


class CoverLetterBuilderAgent:
    def build(self, user_data, job_title, required_skills):
        prompt = f"""You are a professional cover letter writer. Create a tailored cover letter for a {job_title} position.

User details:
- Name: {user_data.get('name', '')}
- Email: {user_data.get('email', '')}
- Phone: {user_data.get('phone', '')}
- Location: {user_data.get('location', '')}
- Professional Summary: {user_data.get('summary', '')}
- Work Experience: {user_data.get('experience', '')}
- Education: {user_data.get('education', '')}
- Key Achievements: {user_data.get('achievements', '')}

Key skills required for this role: {", ".join(required_skills)}

Generate a professional cover letter in plain text format addressed to the Hiring Manager.
Include:
1. Sender contact info (name, phone, email, location)
2. Date
3. Hiring Manager and company placeholder
4. Opening paragraph expressing interest in the {job_title} position
5. Body paragraph connecting the user's experience and achievements to the role requirements
6. Closing paragraph expressing enthusiasm and requesting an interview
7. Sincerely, name

Make it compelling, specific, and tailored. Use professional language.

Return ONLY the cover letter text, no markdown fences, no extra commentary."""
        return _call_llm(prompt)


class SkillAutocompleteAgent:
    def suggest(self, partial, max_results=5):
        if not partial or len(partial.strip()) < 1:
            return []
        prompt = f"""Given the partial text "{partial}", suggest {max_results} common professional skills or skill phrases that start with or closely relate to this text.

Examples of professional skills: Python, Java, Project Management, Data Analysis, Machine Learning, JavaScript, React, AWS, Docker, Kubernetes, SQL, Communication, Leadership, etc.

Return ONLY valid JSON as a simple array of strings, no markdown, no code fences, no extra text:
["skill1", "skill2", "skill3", ...]"""
        try:
            return _call_llm(prompt, response_schema=True)[:max_results]
        except Exception:
            return []


class ParentOrchestrator:
    def __init__(self):
        self.skill_matcher = SkillMatcherAgent()
        self.cv_builder = CvBuilderAgent()
        self.cover_letter_builder = CoverLetterBuilderAgent()
        self.autocomplete = SkillAutocompleteAgent()

    def match_skills(self, skills):
        return self.skill_matcher.match(skills)

    def get_skills_for_title(self, title):
        return self.skill_matcher.get_skills_for_title(title)

    def build_cv(self, user_data, job_title, required_skills):
        return self.cv_builder.build(user_data, job_title, required_skills)

    def build_cover_letter(self, user_data, job_title, required_skills):
        return self.cover_letter_builder.build(user_data, job_title, required_skills)

    def autocomplete_skill(self, partial):
        return self.autocomplete.suggest(partial)
