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
ASSET_DIR = DOCS_DIR / "assets"
DASHBOARD_RELEASE = "20260724-together1"

TRACKER_PATH = SUMMARY_DIR / "statewide_grade3_ela_rollout_tracker.csv"
ANALOG_PATH = SUMMARY_DIR / "statewide_grade3_ela_below_basic_analog.csv"
REFERENCE_PATH = SUMMARY_DIR / "statewide_grade3_ela_published_reference_bins.csv"
TIERS_PATH = SUMMARY_DIR / "statewide_grade3_ela_tiers.csv"
LOOKER_PATH = SUMMARY_DIR / "state_assessment_vs_naep_looker_enriched.csv"
METADATA_PATH = SUMMARY_DIR / "metadata" / "statewide_grade3_ela_sources.json"
NAEP_DOWNLOAD_FILENAME = "naep_2024_grade4_reading_achievement_levels.csv"
NAEP_LEVEL_METRICS = {
    "Percent Below Basic": ("below_basic", "Below Basic"),
    "Percent Basic": ("basic", "Basic"),
    "Percent Proficient": ("proficient", "Proficient"),
    "Percent Advanced": ("advanced", "Advanced"),
}
NAEP_LEVEL_IDS = tuple(level_id for level_id, _ in NAEP_LEVEL_METRICS.values())

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

# Exact-tier records use state-specific names for the proficiency threshold.
# Michigan also publishes additive lower tiers, so its combined value can be
# calculated from the official Proficient or Advanced share.
PROFICIENCY_FIELD_BY_STATE = {
    "AK": "official_statewide_grade3_ela_advanced_or_proficient_pct",
    "AL": "official_statewide_grade3_ela_percent_proficient_pct",
    "AR": "official_statewide_grade3_ela_level3_or_4_pct",
    "AZ": "official_statewide_grade3_ela_percent_proficient_pct",
    "CO": "official_statewide_grade3_ela_met_or_exceeded_pct",
    "CT": "official_statewide_grade3_ela_met_or_exceeded_pct",
    "DC": "official_statewide_grade3_ela_level4_or_5_pct",
    "FL": "official_statewide_grade3_ela_level3_or_above_pct",
    "GA": "official_statewide_grade3_ela_proficient_or_distinguished_pct",
    "ID": "official_statewide_grade3_ela_percent_proficient_pct",
    "IN": "official_statewide_grade3_ela_at_or_above_proficiency_pct",
    "KS": "official_statewide_grade3_ela_percent_proficient_pct",
    "KY": "official_statewide_grade3_reading_proficient_or_distinguished_pct",
    "LA": "official_statewide_grade3_ela_mastery_or_advanced_pct",
    "MA": "official_statewide_grade3_ela_met_or_exceeded_pct",
    "MD": "official_statewide_grade3_ela_proficient_pct",
    "ME": "official_statewide_grade3_ela_percent_proficient_pct",
    "MI": "official_statewide_grade3_ela_percent_proficient_pct",
    "MN": "official_statewide_grade3_ela_percent_proficient_pct",
    "MO": "official_statewide_grade3_ela_percent_proficient_pct",
    "MS": "official_statewide_grade3_ela_proficient_or_advanced_pct",
    "MT": "official_statewide_grade3_ela_percent_proficient_pct",
    "ND": "official_statewide_grade3_ela_percent_proficient_pct",
    "NE": "official_statewide_grade3_ela_percent_proficient_pct",
    "NJ": "official_statewide_grade3_ela_level4_or_5_pct",
    "NV": "official_statewide_grade3_ela_percent_proficient_pct",
    "NY": "official_statewide_grade3_ela_level3_or_4_pct",
    "OK": "official_statewide_grade3_ela_percent_proficient_pct",
    "OR": "official_statewide_grade3_ela_percent_proficient_pct",
    "PA": "official_statewide_grade3_ela_proficient_or_advanced_pct",
    "RI": "official_statewide_grade3_ela_met_or_exceeded_pct",
    "SC": "official_statewide_grade3_ela_meets_or_exceeds_pct",
    "SD": "official_statewide_grade3_ela_percent_proficient_pct",
    "TN": "official_statewide_grade3_ela_met_or_exceeded_pct",
    "TX": "official_statewide_grade3_rla_meets_or_above_pct",
    "UT": "official_statewide_grade3_ela_percent_proficient_pct",
    "VT": "official_statewide_grade3_ela_percent_proficient_pct",
    "WA": "official_statewide_grade3_ela_level3_or_4_tested_only_pct",
    "WI": "official_statewide_grade3_ela_meeting_or_advanced_tested_only_pct",
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
            bins.append(
                {
                    "label": label,
                    "value": value,
                    "isBelowBasicAnalog": False,
                    "isBelowProficiency": False,
                }
            )
    return bins


def tier_bins(rows: list[dict[str, str]]) -> list[dict[str, object]]:
    return [
        {
            "label": row["tier_label"].strip(),
            "value": as_number(row["pct_students"]),
            "isBelowBasicAnalog": row["is_below_basic_analog"].strip().lower() == "true",
            "isBelowProficiency": False,
        }
        for row in sorted(rows, key=lambda item: int(item["tier_rank"]))
    ]


def state_proficiency_value(
    state_code: str,
    analog: dict[str, str],
    analog_value: float,
) -> float:
    field = PROFICIENCY_FIELD_BY_STATE.get(state_code)
    if field is None:
        return round(100.0 - analog_value, 2)
    value = as_number(analog.get(field))
    if value is None:
        raise ValueError(f"Missing official proficiency value for {state_code}: {field}")
    return value


def annotate_state_bins(
    state_code: str,
    status: str,
    bins: list[dict[str, object]],
    analog_label: str,
    analog_value: float,
    not_proficient_value: float,
) -> None:
    for bin_item in bins:
        if (
            str(bin_item["label"]).casefold() == analog_label.casefold()
            and abs(float(bin_item["value"]) - analog_value) <= 0.02
        ):
            bin_item["isBelowBasicAnalog"] = True

    # Exact tiers and the additive Michigan/North Carolina source bins are
    # ordered from lowest to highest. Mark the prefix that best reconstructs
    # the state-published not-proficient share.
    if status == "covered_exact_tiers" or state_code in {"MI", "NC"}:
        candidates: list[tuple[float, int]] = []
        running_total = 0.0
        for index, bin_item in enumerate(bins[:-1], start=1):
            running_total += float(bin_item["value"])
            candidates.append((abs(running_total - not_proficient_value), index))
        if not candidates:
            raise ValueError(f"No lower-tier bins available for {state_code}")
        difference, prefix_length = min(candidates)
        if difference > 1.1:
            raise ValueError(
                f"Published lower tiers for {state_code} do not reconstruct the "
                f"not-proficient share; difference is {difference:.2f} points."
            )
        for bin_item in bins[:prefix_length]:
            bin_item["isBelowProficiency"] = True
    elif status == "covered_source_bins":
        for bin_item in bins:
            if bin_item["isBelowBasicAnalog"]:
                bin_item["isBelowProficiency"] = True


def build_naep_lookup(
    rows: list[dict[str, str]],
) -> dict[str, object]:
    state_values: dict[str, float] = {}
    state_below_proficient: dict[str, float] = {}
    state_levels: dict[str, dict[str, dict[str, object]]] = {}
    national_value = None
    national_below_proficient = None
    national_levels: dict[str, dict[str, object]] = {}
    source_url = ""
    source_page_url = ""
    for row in rows:
        metric_id = row.get("metric_id") or row.get("metric_family") or ""
        if not metric_id.startswith("naep_"):
            continue
        value = as_number(row.get("value"))
        if value is None:
            continue
        source_url = source_url or row.get("source_url", "").strip()
        source_page_url = source_page_url or row.get("source_page_url", "").strip()
        role = row.get("comparison_role")
        metric = row.get("metric", "")
        state_code = row["state_code"]

        if metric == "Percent Below Proficient":
            if role == "naep_state":
                state_below_proficient[state_code] = value
            elif role == "naep_national_public_benchmark":
                national_below_proficient = value
            continue

        level_spec = NAEP_LEVEL_METRICS.get(metric)
        if level_spec is None:
            continue
        level_id, label = level_spec
        level = {"id": level_id, "label": label, "value": value}
        if role == "naep_state":
            state_levels.setdefault(state_code, {})[level_id] = level
            if level_id == "below_basic":
                state_values[state_code] = value
        elif role == "naep_national_public_benchmark":
            national_levels[level_id] = level
            if level_id == "below_basic":
                national_value = value

    return {
        "stateValues": state_values,
        "stateBelowProficient": state_below_proficient,
        "stateLevels": {
            state_code: [levels[level_id] for level_id in NAEP_LEVEL_IDS if level_id in levels]
            for state_code, levels in state_levels.items()
        },
        "nationalValue": national_value,
        "nationalBelowProficient": national_below_proficient,
        "nationalLevels": [
            national_levels[level_id]
            for level_id in NAEP_LEVEL_IDS
            if level_id in national_levels
        ],
        "sourceUrl": source_url,
        "sourcePageUrl": source_page_url,
    }


def write_dashboard_csv(states: list[dict[str, object]], destination: Path) -> None:
    fieldnames = [
        "state",
        "state_name",
        "data_quality",
        "assessment",
        "school_year",
        "reported_measure",
        "below_basic_analog_pct",
        "not_meeting_proficiency_pct",
        "state_proficiency_pct",
        "naep_2024_grade4_reading_below_basic_pct",
        "naep_2024_grade4_reading_below_proficient_pct",
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
                    "not_meeting_proficiency_pct": state["notProficientValue"],
                    "state_proficiency_pct": state["proficiencyValue"],
                    "naep_2024_grade4_reading_below_basic_pct": state["naepValue"],
                    "naep_2024_grade4_reading_below_proficient_pct": state[
                        "naepBelowProficientValue"
                    ],
                    "source_page_url": state["sourcePageUrl"],
                }
            )


def write_naep_csv(
    states: list[dict[str, object]],
    national_value: float,
    national_below_proficient: float,
    national_levels: list[dict[str, object]],
    source_page_url: str,
    destination: Path,
) -> None:
    national_by_level = {str(level["id"]): level["value"] for level in national_levels}
    fieldnames = [
        "state",
        "state_name",
        "year",
        "grade",
        "subject",
        "state_below_basic_pct",
        "state_basic_pct",
        "state_proficient_pct",
        "state_advanced_pct",
        "state_below_proficient_pct",
        "national_public_below_basic_pct",
        "national_public_basic_pct",
        "national_public_proficient_pct",
        "national_public_advanced_pct",
        "national_public_below_proficient_pct",
        "below_basic_difference_from_national_percentage_points",
        "source_page_url",
    ]
    with destination.open("w", newline="", encoding="utf-8") as output:
        writer = csv.DictWriter(output, fieldnames=fieldnames, lineterminator="\n")
        writer.writeheader()
        for state in states:
            value = state["naepValue"]
            state_by_level = {
                str(level["id"]): level["value"] for level in state["naepLevels"]
            }
            writer.writerow(
                {
                    "state": state["code"],
                    "state_name": state["name"],
                    "year": 2024,
                    "grade": 4,
                    "subject": "Reading",
                    "state_below_basic_pct": state_by_level["below_basic"],
                    "state_basic_pct": state_by_level["basic"],
                    "state_proficient_pct": state_by_level["proficient"],
                    "state_advanced_pct": state_by_level["advanced"],
                    "state_below_proficient_pct": state["naepBelowProficientValue"],
                    "national_public_below_basic_pct": national_by_level["below_basic"],
                    "national_public_basic_pct": national_by_level["basic"],
                    "national_public_proficient_pct": national_by_level["proficient"],
                    "national_public_advanced_pct": national_by_level["advanced"],
                    "national_public_below_proficient_pct": national_below_proficient,
                    "below_basic_difference_from_national_percentage_points": round(
                        float(value) - national_value, 2
                    ),
                    "source_page_url": source_page_url,
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
    naep_lookup = build_naep_lookup(read_csv(LOOKER_PATH))
    naep_by_state = naep_lookup["stateValues"]
    naep_below_proficient_by_state = naep_lookup["stateBelowProficient"]
    naep_levels_by_state = naep_lookup["stateLevels"]
    national_naep = naep_lookup["nationalValue"]
    national_naep_below_proficient = naep_lookup["nationalBelowProficient"]
    national_naep_levels = naep_lookup["nationalLevels"]
    naep_source_url = naep_lookup["sourceUrl"]
    naep_source_page_url = naep_lookup["sourcePageUrl"]
    metadata = json.loads(METADATA_PATH.read_text(encoding="utf-8"))

    exact_codes = {
        row["state"] for row in tracker_rows if row["status"] == "covered_exact_tiers"
    }
    missing_proficiency_fields = exact_codes - set(PROFICIENCY_FIELD_BY_STATE)
    if missing_proficiency_fields:
        raise ValueError(
            "Exact-tier states need an explicit proficiency threshold: "
            f"{', '.join(sorted(missing_proficiency_fields))}"
        )

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

        analog_label = analog["below_basic_analog_label"]
        analog_value = as_number(analog["below_basic_analog_pct"])
        if analog_value is None:
            raise ValueError(f"No numeric statewide below-basic analog for {code}")
        proficiency_value = state_proficiency_value(code, analog, analog_value)
        not_proficient_value = round(100.0 - proficiency_value, 2)
        annotate_state_bins(
            code,
            tracker["status"],
            bins,
            analog_label,
            analog_value,
            not_proficient_value,
        )

        has_breakdown = tracker["status"] == "covered_exact_tiers" or code == "MI"
        if tracker["status"] == "covered_exact_tiers" or code in {"MI", "NC"}:
            # The headline is literally the published below-proficiency buckets
            # together. This preserves state rounding instead of forcing the
            # tiers to equal exactly 100 minus the proficiency rate.
            not_proficient_value = round(
                sum(
                    float(bin_item["value"])
                    for bin_item in bins
                    if bin_item["isBelowProficiency"]
                ),
                2,
            )
        if not 0 <= not_proficient_value <= 100:
            raise ValueError(f"Invalid not-proficient value for {code}: {not_proficient_value}")
        other_below_proficient_value = (
            round(not_proficient_value - analog_value, 2)
            if has_breakdown
            else None
        )
        other_labels = [
            str(bin_item["label"])
            for bin_item in bins
            if bin_item["isBelowProficiency"] and not bin_item["isBelowBasicAnalog"]
        ]
        other_below_proficient_label = (
            " + ".join(other_labels)
            if other_labels
            else "No additional below-proficiency tier"
        )

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
                "analogLabel": analog_label,
                "analogValue": analog_value,
                "proficiencyValue": proficiency_value,
                "notProficientLabel": "Not meeting proficiency",
                "notProficientValue": not_proficient_value,
                "hasBelowProficiencyBreakdown": has_breakdown,
                "otherBelowProficientLabel": other_below_proficient_label,
                "otherBelowProficientValue": other_below_proficient_value,
                "naepValue": naep_by_state.get(code),
                "naepBelowProficientValue": naep_below_proficient_by_state.get(code),
                "naepLevels": naep_levels_by_state.get(code, []),
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

    if counts["jurisdictions"] != 51:
        raise ValueError(
            f"Dashboard must include all 50 states and DC; found {counts['jurisdictions']} jurisdictions."
        )
    if len({state["code"] for state in states}) != counts["jurisdictions"]:
        raise ValueError("Dashboard tracker contains duplicate state or jurisdiction codes.")
    categorized_count = counts["exact"] + counts["state"] + counts["federal"]
    if categorized_count != counts["jurisdictions"]:
        raise ValueError(
            "Every dashboard jurisdiction must map to exactly one source-quality category; "
            f"categorized {categorized_count} of {counts['jurisdictions']}."
        )

    state_codes = {state["code"] for state in states}
    missing_naep = sorted(state_codes - set(naep_by_state))
    missing_naep_below_proficient = sorted(
        state_codes - set(naep_below_proficient_by_state)
    )
    missing_naep_levels = sorted(state_codes - set(naep_levels_by_state))
    if (
        national_naep is None
        or national_naep_below_proficient is None
        or len(national_naep_levels) != len(NAEP_LEVEL_IDS)
        or missing_naep
        or missing_naep_below_proficient
        or missing_naep_levels
    ):
        raise ValueError(
            "NAEP data must include all achievement levels and Below Proficient for "
            "the national public benchmark and all 51 jurisdictions; missing Below Basic: "
            f"{', '.join(missing_naep) or 'none'}; missing Below Proficient: "
            f"{', '.join(missing_naep_below_proficient) or 'none'}; missing levels: "
            f"{', '.join(missing_naep_levels) or 'none'}"
        )

    for state in states:
        levels = state["naepLevels"]
        if [level["id"] for level in levels] != list(NAEP_LEVEL_IDS):
            raise ValueError(f"NAEP achievement levels are incomplete for {state['code']}.")
        level_total = sum(float(level["value"]) for level in levels)
        if abs(level_total - 100.0) > 0.1:
            raise ValueError(
                f"NAEP achievement levels for {state['code']} sum to {level_total}, not 100."
            )
        below_proficient = float(levels[0]["value"]) + float(levels[1]["value"])
        if abs(below_proficient - float(state["naepBelowProficientValue"])) > 0.02:
            raise ValueError(f"NAEP Below Proficient is inconsistent for {state['code']}.")

        if state["hasBelowProficiencyBreakdown"]:
            reconstructed = float(state["analogValue"]) + float(
                state["otherBelowProficientValue"]
            )
            if abs(reconstructed - float(state["notProficientValue"])) > 0.02:
                raise ValueError(
                    f"State below-proficiency breakdown is inconsistent for {state['code']}."
                )

    national_level_total = sum(float(level["value"]) for level in national_naep_levels)
    if abs(national_level_total - 100.0) > 0.1:
        raise ValueError(
            f"National NAEP achievement levels sum to {national_level_total}, not 100."
        )

    new_hampshire = next(state for state in states if state["code"] == "NH")
    if (
        new_hampshire["quality"] != "state"
        or new_hampshire["analogValue"] != 51.0
        or not new_hampshire["bins"]
        or new_hampshire["bins"][0]["value"] != 49.0
    ):
        raise ValueError("New Hampshire must be an official state proficiency source with 49% proficient.")

    massachusetts = next(state for state in states if state["code"] == "MA")
    if (
        massachusetts["notProficientValue"] != 58.0
        or massachusetts["analogValue"] != 19.0
        or massachusetts["otherBelowProficientValue"] != 39.0
    ):
        raise ValueError("Massachusetts must show 19% + 39% = 58% not meeting proficiency.")

    michigan = next(state for state in states if state["code"] == "MI")
    if michigan["notProficientValue"] != 61.1:
        raise ValueError("Michigan must combine Not Proficient and Partially Proficient.")

    DATA_DIR.mkdir(parents=True, exist_ok=True)
    DOWNLOADS_DIR.mkdir(parents=True, exist_ok=True)
    ASSET_DIR.mkdir(parents=True, exist_ok=True)

    dashboard_csv_path = DOWNLOADS_DIR / "state_assessment_dashboard_results.csv"
    write_dashboard_csv(states, dashboard_csv_path)
    naep_csv_path = DOWNLOADS_DIR / NAEP_DOWNLOAD_FILENAME
    write_naep_csv(
        states,
        national_naep,
        national_naep_below_proficient,
        national_naep_levels,
        naep_source_page_url,
        naep_csv_path,
    )
    for source in DOWNLOAD_FILES:
        shutil.copyfile(source, DOWNLOADS_DIR / source.name)
    shutil.copyfile(
        DOCS_DIR / "app.js",
        ASSET_DIR / f"dashboard-{DASHBOARD_RELEASE}.js",
    )
    shutil.copyfile(
        DOCS_DIR / "styles.css",
        ASSET_DIR / f"dashboard-{DASHBOARD_RELEASE}.css",
    )

    payload = {
        "title": "State Assessment Data Monitor",
        "buildDate": metadata["build_date"],
        "scope": "Statewide Grade 3 English language arts",
        "counts": counts,
        "nationalNaepValue": national_naep,
        "naep": {
            "year": 2024,
            "grade": 4,
            "subject": "Reading",
            "metric": "Percent Below Basic",
            "nationalValue": national_naep,
            "nationalBelowProficientValue": national_naep_below_proficient,
            "nationalLevels": national_naep_levels,
            "sourceUrl": naep_source_url,
            "sourcePageUrl": naep_source_page_url,
            "jurisdictions": len(naep_by_state),
            "downloadFile": f"downloads/{NAEP_DOWNLOAD_FILENAME}",
        },
        "states": states,
        "downloads": [
            {
                "label": "Dashboard results",
                "file": "downloads/state_assessment_dashboard_results.csv",
                "description": "Combined not-meeting result and lowest-tier context for every jurisdiction.",
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
            {
                "label": "NAEP Grade 4 Reading",
                "file": f"downloads/{NAEP_DOWNLOAD_FILENAME}",
                "description": "2024 achievement levels and Below Proficient for every state and DC, with the national benchmark.",
            },
        ],
    }
    payload_text = json.dumps(payload, indent=2, ensure_ascii=True) + "\n"
    for destination in [
        DATA_DIR / "dashboard.json",
        DATA_DIR / f"dashboard-{DASHBOARD_RELEASE}.json",
    ]:
        destination.write_text(payload_text, encoding="utf-8")

    print(
        "Dashboard data built: "
        f"{counts['statePublished']} state-published, {counts['federal']} federal proxy, "
        f"{counts['jurisdictions']} jurisdictions."
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
