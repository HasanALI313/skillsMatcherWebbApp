import os
import requests

from webapp.config import ADZUNA_APP_ID, ADZUNA_API_KEY, ADZUNA_COUNTRY

BASE_URL = "https://api.adzuna.com/v1/api/jobs"


def search_jobs(query, results_per_page=10):
    url = f"{BASE_URL}/{ADZUNA_COUNTRY}/search/1"
    params = {
        "app_id": ADZUNA_APP_ID,
        "app_key": ADZUNA_API_KEY,
        "results_per_page": results_per_page,
        "what": query,
        "content-type": "application/json",
    }
    try:
        resp = requests.get(url, params=params, timeout=10)
        resp.raise_for_status()
        data = resp.json()
        return data.get("results", [])
    except Exception as e:
        return []
