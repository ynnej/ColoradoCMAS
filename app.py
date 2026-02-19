#!/usr/bin/env python3
"""Streamlit dashboard for Colorado CMAS ELA Grade 3 district data."""

from __future__ import annotations

from pathlib import Path

import pandas as pd
import streamlit as st

DATA_PATH = Path("data/cmas_ela_grade3_district.csv")


@st.cache_data(show_spinner=False)
def load_data(path: str) -> pd.DataFrame:
    df = pd.read_csv(path)
    for col in [
        "grade_3_percent_met_or_exceeded_district",
        "grade_3_participation_rate_district",
    ]:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce")
    return df


def apply_filters(
    df: pd.DataFrame,
    min_participation: float,
    max_met: float,
    district_search: str,
) -> pd.DataFrame:
    out = df.copy()

    if "grade_3_participation_rate_district" in out.columns:
        out = out[
            out["grade_3_participation_rate_district"].isna()
            | (out["grade_3_participation_rate_district"] >= min_participation)
        ]

    if "grade_3_percent_met_or_exceeded_district" in out.columns:
        out = out[
            out["grade_3_percent_met_or_exceeded_district"].isna()
            | (out["grade_3_percent_met_or_exceeded_district"] <= max_met)
        ]

    district_search = district_search.strip().lower()
    if district_search and "district_name" in out.columns:
        out = out[out["district_name"].fillna("").str.lower().str.contains(district_search, regex=False)]

    return out


def summary_stats(df: pd.DataFrame) -> dict[str, float | int]:
    return {
        "district_count": int(len(df)),
        "avg_met": float(df["grade_3_percent_met_or_exceeded_district"].mean(skipna=True))
        if "grade_3_percent_met_or_exceeded_district" in df.columns
        else float("nan"),
        "avg_participation": float(df["grade_3_participation_rate_district"].mean(skipna=True))
        if "grade_3_participation_rate_district" in df.columns
        else float("nan"),
    }


def main() -> None:
    st.set_page_config(page_title="Colorado CMAS District Dashboard", layout="wide")
    st.title("Colorado CMAS ELA Grade 3 District Dashboard")

    if not DATA_PATH.exists():
        st.error(f"Missing data file: {DATA_PATH}. Run `python fetch_cmas_co.py` first.")
        st.stop()

    df = load_data(str(DATA_PATH))

    st.sidebar.header("Filters")
    min_participation = st.sidebar.slider(
        "Min participation rate (%)",
        min_value=0.0,
        max_value=100.0,
        value=0.0,
        step=0.5,
    )
    max_met = st.sidebar.slider(
        "Max % met/exceeded (need)",
        min_value=0.0,
        max_value=100.0,
        value=100.0,
        step=0.5,
    )
    district_search = st.sidebar.text_input("District name search", value="")

    filtered = apply_filters(df, min_participation, max_met, district_search)

    stats = summary_stats(filtered)
    c1, c2, c3 = st.columns(3)
    c1.metric("Districts (filtered)", f"{stats['district_count']:,}")
    c2.metric("Avg % Met/Exceeded", f"{stats['avg_met']:.1f}" if pd.notna(stats["avg_met"]) else "N/A")
    c3.metric(
        "Avg Participation",
        f"{stats['avg_participation']:.1f}" if pd.notna(stats["avg_participation"]) else "N/A",
    )

    st.subheader("District Table")
    st.dataframe(filtered, use_container_width=True, hide_index=True)

    csv_bytes = filtered.to_csv(index=False).encode("utf-8")
    st.download_button(
        "Download filtered CSV",
        data=csv_bytes,
        file_name="cmas_ela_grade3_district_filtered.csv",
        mime="text/csv",
    )


if __name__ == "__main__":
    main()
