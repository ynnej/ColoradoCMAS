from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any

import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry


def build_session(user_agent: str = "StateAssessmentDatasets/1.0") -> requests.Session:
    retry = Retry(
        total=5,
        backoff_factor=1.0,
        status_forcelist=(429, 500, 502, 503, 504),
        allowed_methods=("GET", "POST", "HEAD"),
        respect_retry_after_header=True,
    )
    adapter = HTTPAdapter(max_retries=retry)
    session = requests.Session()
    session.mount("https://", adapter)
    session.mount("http://", adapter)
    session.headers.update(
        {
            "User-Agent": user_agent,
            "Accept": "*/*",
        }
    )
    return session


def ensure_parent(path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)


def write_json(path: Path, payload: dict[str, Any]) -> None:
    ensure_parent(path)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def slugify_column(name: object) -> str:
    text = str(name).replace("\n", " ").strip().lower()
    text = text.replace("%", " percent ")
    text = re.sub(r"[^a-z0-9]+", "_", text)
    return re.sub(r"_+", "_", text).strip("_")


def normalize_code(value: object, width: int) -> str | None:
    if value is None:
        return None
    text = str(value).strip()
    if not text:
        return None
    digits = re.sub(r"\D", "", text)
    if not digits:
        return None
    return digits.zfill(width)


def normalize_grade(value: object) -> str | None:
    if value is None:
        return None
    text = str(value).strip()
    if not text:
        return None
    return text.zfill(2) if text.isdigit() else text


def clean_number(value: object) -> float | None:
    if value is None:
        return None
    text = str(value).strip()
    if not text:
        return None
    normalized = text.replace(",", "").replace("%", "").strip()
    if normalized in {".", "-1", "--", "- -", "N/A", "n/a", "NA", "na"}:
        return None
    try:
        return float(normalized)
    except ValueError:
        return None
