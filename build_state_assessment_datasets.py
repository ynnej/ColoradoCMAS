#!/usr/bin/env python3
"""Build a small repository of state-specific assessment datasets."""

from __future__ import annotations

import argparse
from pathlib import Path

import pandas as pd

from state_assessment_data.colorado_cmas import build as build_colorado
from state_assessment_data.common import build_session
from state_assessment_data.texas_staar import build as build_texas


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Build the state assessment dataset repository.")
    parser.add_argument(
        "--co-raw-workbook",
        type=Path,
        default=None,
        help="Optional local path to the Colorado CMAS workbook. If omitted, the builder downloads it.",
    )
    parser.add_argument(
        "--tx-raw-csv",
        type=Path,
        default=None,
        help="Optional local path to the Texas TAPR STAAR CSV. If omitted, the builder downloads it.",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    repo_root = Path(__file__).resolve().parent
    session = build_session()

    artifacts: list[dict[str, str]] = []
    artifacts.extend(build_colorado(repo_root, session=session, raw_workbook=args.co_raw_workbook))
    artifacts.extend(build_texas(repo_root, session=session, raw_csv=args.tx_raw_csv))

    catalog_path = repo_root / "datasets/catalog.csv"
    catalog_path.parent.mkdir(parents=True, exist_ok=True)
    pd.DataFrame(artifacts).sort_values(
        by=["state", "program", "reporting_period", "kind", "path"], kind="stable"
    ).to_csv(catalog_path, index=False)

    print(f"Wrote {catalog_path.relative_to(repo_root)}")
    for artifact in artifacts:
        print(f"- {artifact['path']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
