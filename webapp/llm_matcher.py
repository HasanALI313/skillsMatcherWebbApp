import json
from google import genai
from config import GEMINI_API_KEY, GEMINI_MODEL

client = genai.Client(api_key=GEMINI_API_KEY)

MATCH_PROMPT = """Given these 5 skills: {skills}

Suggest the top 3 job titles that best match these skills.
For each job title, list exactly 10 key skills required for that role.

Return ONLY valid JSON in this exact format (no markdown, no code fences, no extra text):
[{{"title": "Job Title", "skills": ["skill1", "skill2", "skill3", "skill4", "skill5", "skill6", "skill7", "skill8", "skill9", "skill10"]}}, ...]"""

SKILLS_PROMPT = """Given this job title: "{title}"

List exactly 10 key skills required for that role.

Return ONLY valid JSON in this exact format (no markdown, no code fences, no extra text):
{{"skills": ["skill1", "skill2", "skill3", "skill4", "skill5", "skill6", "skill7", "skill8", "skill9", "skill10"]}}"""

def match_top_3(user_skills):
    prompt = MATCH_PROMPT.format(skills=", ".join(user_skills))
    try:
        resp = client.models.generate_content(model=GEMINI_MODEL, contents=prompt)
        raw = resp.text.strip()
        raw = raw.removeprefix("```json").removeprefix("```").removesuffix("```").strip()
        data = json.loads(raw)
        results = []
        for entry in data[:3]:
            title = entry["title"]
            required = entry["skills"][:10]
            score = len(set(s.lower() for s in user_skills) & set(s.lower() for s in required))
            results.append((title, score, required))
        return results
    except Exception as e:
        raise RuntimeError(f"LLM matching failed: {e}")

def get_job_skills(title):
    prompt = SKILLS_PROMPT.format(title=title)
    try:
        resp = client.models.generate_content(model=GEMINI_MODEL, contents=prompt)
        raw = resp.text.strip()
        raw = raw.removeprefix("```json").removeprefix("```").removesuffix("```").strip()
        data = json.loads(raw)
        return data["skills"][:10]
    except Exception as e:
        return []
