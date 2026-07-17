"""Shared helpers: polite HTTP fetching with a local cache, and the team-name mapping."""

import csv
import pathlib
import time

import requests

PROJECT_ROOT = pathlib.Path(__file__).resolve().parent.parent
RAW_DIR = PROJECT_ROOT / "data" / "raw"
DATA_DIR = PROJECT_ROOT / "data"
MAPPING_FILE = PROJECT_ROOT / "data" / "mappings" / "team_names.csv"

USER_AGENT = "franchise-tracker/0.1 (student research project)"
REQUEST_DELAY_SECONDS = 3


def polite_get(url, cache_name):
    """Fetch a URL once and cache the body in data/raw/.

    Re-runs read the cache instead of hitting the site again. The delay runs
    before every real network request so consecutive fetches are spaced out.
    """
    RAW_DIR.mkdir(parents=True, exist_ok=True)
    cache_file = RAW_DIR / cache_name
    if cache_file.exists():
        return cache_file.read_text(encoding="utf-8")

    time.sleep(REQUEST_DELAY_SECONDS)
    response = requests.get(url, headers={"User-Agent": USER_AGENT}, timeout=30)
    response.raise_for_status()
    cache_file.write_text(response.text, encoding="utf-8")
    return response.text


def load_team_mapping():
    """Return two lookup dicts from data/mappings/team_names.csv:

    by_api_code:  euroleague_api_code -> canonical_name
    by_basketnews: basketnews_name    -> canonical_name
    """
    by_api_code = {}
    by_basketnews = {}
    with open(MAPPING_FILE, newline="", encoding="utf-8") as f:
        for row in csv.DictReader(f):
            canonical = row["canonical_name"].strip()
            if row["euroleague_api_code"].strip():
                by_api_code[row["euroleague_api_code"].strip()] = canonical
            if row["basketnews_name"].strip():
                by_basketnews[row["basketnews_name"].strip()] = canonical
    return by_api_code, by_basketnews
