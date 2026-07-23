#!/usr/bin/env python3
"""Build the static GitHub Pages data bundle from the assessment outputs."""

from __future__ import annotations

import csv
import json
import shutil
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parent
SUMMARY_DIR = REPO_ROOT / "datasets" / "summary"
DOCS_DIR = REPO_ROOT / "docs"
DATA_DIR = DOCS_DIR / "data"
DOWNLOADS_DIR = DOCS_DIR / "downloads"

TRACKER_PATH = SUMMARY_DIR / "statewide_grade3_ela_rollout_tracker.csv"
ANALOG_PATH = SUMMARY_DIR / "statewide_grade3_ela_below_basic_analog.csv"
REFERENCE_PATH = SUMMARY_DIR / "statewide_grade3_ela_published_reference_bins.csv"
TIERS_PATH = SUMMARY_DIR / "statewide_grade3_ela_tiers.csv"
LOOKER_PATH = SUMMARY_DIR / "state_assessment_vs_naep_looker_enriched.csv"
METADATA_PATH = SUMMARY_DIR / "metadata" / "statewide_grade3_ela_sources.json"

STATUS_CONFIG = {
    "covered_exact_tiers": {
        "key": "exact",
        "label": "Exact state tiers",
        "short_label": "Exact tiers",
    },
    "covered_source_bins": {
        "key": "state",
        "label": "Official state source bins",
        "short_label": "State source",
    },
    "covered_official_proficiency_proxy": {
        "key": "state",
        "label": "Official state proficiency",
        "short_label": "State source",
    },
    "covered_federal_proficiency_proxy": {
        "key": "federal",
        "label": "Ed Data Express proxy",
        "short_label": "Federal proxy",
    },
}

DOWNLOAD_FILES = [
    TRACKER_PATH,
    ANALOG_PATH,
    REFERENCE_PATH,
    TIERS_PATH,
    LOOKER_PATH,
]


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8-sig") as source:
        return list(csv.DictReader(source))


def as_number(value: str | None) -> float | None:
    if value is None or not value.strip():
        return None
    return round(float(value), 2)


def reference_bins(row: dict[str, str] | None) -> list[dict[str, object]]:
    if row is None:
        return []
    bins = []
    for index in range(1, 6):
        label = row.get(f"source_bin_{index}_label", "").strip()
        value = as_number(row.get(f"source_bin_{index}_pct"))
        if label and value is not None:
            bins.append({"label": label, "value": value})
    return bins


def tier_bins(rows: list[dict[str, str]]) -> list[dict[str, object]]:
    return [
        {
            "label": row["tier_label"].strip(),
            "value": as_number(row["pct_students"]),
            "isBelowBasicAnalog": row["is_below_basic_analog"].strip().lower() == "true",
        }
        for row in sorted(rows, key=lambda item: int(item["tier_rank"]))
    ]


def build_naep_lookup(rows: list[dict[str, str]]) -> tuple[dict[str, float], float | None]:
    state_values: dict[str, float] = {}
    national_value = None
    for row in rows:
        if row.get("metric_id") != "naep_below_basic":
            continue
        value = as_number(row.get("value"))
        if value is None:
            continue
        if row.get("comparison_role") == "naep_state":
            state_values[row["state_code"]] = value
        elif row.get("comparison_role") == "naep_national_public_benchmark":
            national_value = value
    return state_values, national_value


def write_dashboard_csv(states: list[dict[str, object]], destination: Path) -> None:
    fieldnames = [
        "state",
        "state_name",
        "data_quality",
        "assessment",
        "school_year",
        "reported_measure",
        "below_basic_analog_pct",
        "naep_2024_grade4_reading_below_basic_pct",
        "source_page_url",
    ]
    with destination.open("w", newline="", encoding="utf-8") as output:
        writer = csv.DictWriter(output, fieldnames=fieldnames, lineterminator="\n")
        writer.writeheader()
        for state in states:
            writer.writerow(
                {
                    "state": state["code"],
                    "state_name": state["name"],
                    "data_quality": state["qualityLabel"],
                    "assessment": state["assessment"],
                    "school_year": state["schoolYear"],
                    "reported_measure": state["analogLabel"],
                    "below_basic_analog_pct": state["analogValue"],
                    "naep_2024_grade4_reading_below_basic_pct": state["naepValue"],
                    "source_page_url": state["sourcePageUrl"],
                }
            )


def main() -> int:
    required_paths = [TRACKER_PATH, ANALOG_PATH, REFERENCE_PATH, TIERS_PATH, LOOKER_PATH, METADATA_PATH]
    missing = [str(path.relative_to(REPO_ROOT)) for path in required_paths if not path.exists()]
    if missing:
        raise FileNotFoundError(f"Missing dashboard input files: {', '.join(missing)}")

    tracker_rows = read_csv(TRACKER_PATH)
    analog_by_state = {row["state"]: row for row in read_csv(ANALOG_PATH)}
    reference_by_state = {row["state"]: row for row in read_csv(REFERENCE_PATH)}
    tiers_by_state: dict[str, list[dict[str, str]]] = {}
    for row in read_csv(TIERS_PATH):
        tiers_by_state.setdefault(row["state"], []).append(row)
    naep_by_state, national_naep = build_naep_lookup(read_csv(LOOKER_PATH))
    metadata = json.loads(METADATA_PATH.read_text(encoding="utf-8"))

    states: list[dict[str, object]] = []
    for tracker in tracker_rows:
        code = tracker["state"]
        status = STATUS_CONFIG.get(tracker["status"])
        if status is None:
            raise ValueError(f"Unsupported tracker status for {code}: {tracker['status']}")
        analog = analog_by_state.get(code)
        if analog is None:
            raise ValueError(f"No statewide below-basic analog row for {code}")

        bins = tier_bins(tiers_by_state.get(code, []))
        if not bins:
            bins = reference_bins(reference_by_state.get(code))

        states.append(
            {
                "code": code,
                "name": tracker["state_name"],
                "status": tracker["status"],
                "quality": status["key"],
                "qualityLabel": status["label"],
                "qualityShortLabel": status["short_label"],
                "assessment": tracker["assessment"],
                "schoolYear": tracker["school_year"],
                "analogLabel": analog["below_basic_analog_label"],
                "analogValue": as_number(analog["below_basic_analog_pct"]),
                "naepValue": naep_by_state.get(code),
                "sourceNotes": analog["source_notes"],
                "sourceUrl": analog["source_url"],
                "sourcePageUrl": tracker["source_page_url"],
                "bins": bins,
            }
        )

    counts = {
        "jurisdictions": len(states),
        "exact": sum(state["quality"] == "exact" for state in states),
        "state": sum(state["quality"] == "state" for state in states),
        "federal": sum(state["quality"] == "federal" for state in states),
    }
    counts["statePublished"] = counts["exact"] + counts["state"]

    expected_counts = {
        "jurisdictions": 51,
        "exact": 22,
        "state": 7,
        "federal": 22,
        "statePublished": 29,
    }
    if counts != expected_counts:
        raise ValueError(f"Unexpected coverage counts: {counts}; expected {expected_counts}")

    new_hampshire = next(state for state in states if state["code"] == "NH")
    if (
        new_hampshire["quality"] != "state"
        or new_hampshire["analogValue"] != 51.0
        or not new_hampshire["bins"]
        or new_hampshire["bins"][0]["value"] != 49.0
    ):
        raise ValueError("New Hampshire must be an official state proficiency source with 49% proficient.")

    DATA_DIR.mkdir(parents=True, exist_ok=True)
    DOWNLOADS_DIR.mkdir(parents=True, exist_ok=True)

    dashboard_csv_path = DOWNLOADS_DIR / "state_assessment_dashboard_results.csv"
    write_dashboard_csv(states, dashboard_csv_path)
    for source in DOWNLOAD_FILES:
        shutil.copyfile(source, DOWNLOADS_DIR / source.name)

    payload = {
        "title": "State Assessment Data Monitor",
        "buildDate": metadata["build_date"],
        "scope": "Statewide Grade 3 English language arts",
        "counts": counts,
        "nationalNaepValue": national_naep,
        "states": states,
        "downloads": [
            {
                "label": "Dashboard results",
                "file": "downloads/state_assessment_dashboard_results.csv",
                "description": "One concise row per state or jurisdiction.",
            },
            {
                "label": "Coverage tracker",
                "file": f"downloads/{TRACKER_PATH.name}",
                "description": "Source quality, assessment, year, and notes for all jurisdictions.",
            },
            {
                "label": "Below-basic analog",
                "file": f"downloads/{ANALOG_PATH.name}",
                "description": "Cross-state analytical measure and source fields.",
            },
            {
                "label": "Published source bins",
                "file": f"downloads/{REFERENCE_PATH.name}",
                "description": "State-published tiers, bins, or proficiency values.",
            },
            {
                "label": "Exact state tiers",
                "file": f"downloads/{TIERS_PATH.name}",
                "description": "Long-form exact performance tiers where available.",
            },
        ],
    }
    (DATA_DIR / "dashboard.json").write_text(
        json.dumps(payload, indent=2, ensure_ascii=True) + "\n",
        encoding="utf-8",
    )

    print(
        "Dashboard data built: "
        f"{counts['statePublished']} state-published, {counts['federal']} federal proxy, "
        f"{counts['jurisdictions']} jurisdictions."
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
