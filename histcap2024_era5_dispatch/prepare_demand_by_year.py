#!/usr/bin/env python3
"""Prepare one electricity-demand CSV per weather-year scenario."""

from __future__ import annotations

import argparse
import os
from pathlib import Path

import pandas as pd


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Split a multi-year hourly electricity-demand CSV into yearly files "
            "and link each file into resources/<scenario>/electricity_demand.csv."
        )
    )
    parser.add_argument("--source", required=True, type=Path)
    parser.add_argument("--prepared-dir", required=True, type=Path)
    parser.add_argument("--resources-dir", required=True, type=Path)
    parser.add_argument(
        "--scenario-template",
        required=True,
        help="Scenario name template, for example 'histcap2024_era5_weather_year_{year}'.",
    )
    parser.add_argument("--start-year", required=True, type=int)
    parser.add_argument("--end-year", required=True, type=int)
    parser.add_argument(
        "--drop-leap-day",
        action=argparse.BooleanOptionalAction,
        default=True,
        help="Drop February 29 to match PyPSA-Eur enable.drop_leap_day.",
    )
    return parser.parse_args()


def read_demand(path: Path) -> pd.DataFrame:
    raw = pd.read_csv(path)
    if raw.empty:
        raise ValueError(f"Demand file is empty: {path}")

    time_col = raw.columns[0]
    timestamps = pd.to_datetime(raw[time_col], errors="coerce")
    if timestamps.isna().any():
        raise ValueError(f"Could not parse first CSV column as datetimes: {time_col}")

    data = raw.drop(columns=[time_col])
    index = pd.DatetimeIndex(timestamps)
    if index.tz is not None:
        index = index.tz_convert(None)
    data.index = index
    data.index.name = time_col
    return data


def expected_snapshots(year: int, drop_leap_day: bool) -> pd.DatetimeIndex:
    snapshots = pd.date_range(
        f"{year}-01-01 00:00",
        f"{year}-12-31 23:00",
        freq="h",
    )
    if drop_leap_day:
        snapshots = snapshots[~((snapshots.month == 2) & (snapshots.day == 29))]
    return snapshots


def replace_symlink(source: Path, target: Path) -> None:
    target.parent.mkdir(parents=True, exist_ok=True)
    if target.exists() or target.is_symlink():
        target.unlink()
    os.symlink(source, target)


def main() -> int:
    args = parse_args()
    source_file = args.source.resolve()
    prepared_dir = args.prepared_dir.resolve()
    resources_dir = args.resources_dir.resolve()

    if not source_file.is_file():
        raise FileNotFoundError(f"Missing demand file: {source_file}")
    if "{year}" not in args.scenario_template:
        raise ValueError("--scenario-template must contain '{year}'")
    if args.end_year < args.start_year:
        raise ValueError("--end-year must be >= --start-year")

    prepared_dir.mkdir(parents=True, exist_ok=True)
    demand = read_demand(source_file)
    if args.drop_leap_day:
        demand = demand[~((demand.index.month == 2) & (demand.index.day == 29))]

    years = range(args.start_year, args.end_year + 1)
    yearly_outputs = []

    for year in years:
        expected = expected_snapshots(year, args.drop_leap_day)
        yearly = demand[demand.index.year == year]

        if yearly.index.has_duplicates:
            duplicates = yearly.index[yearly.index.duplicated()].unique()[:5]
            raise ValueError(f"Duplicate timestamps for {year}: {list(duplicates)}")

        missing = expected.difference(yearly.index)
        if len(missing):
            raise ValueError(
                f"Demand data for {year} is missing {len(missing)} hourly snapshots. "
                f"First missing timestamp: {missing[0]}"
            )

        yearly = yearly.loc[expected]
        output = prepared_dir / f"electricity_demand_{year}.csv"
        yearly.to_csv(output, index_label=demand.index.name)
        yearly_outputs.append(output)

        scenario_name = args.scenario_template.format(year=year)
        scenario_link = resources_dir / scenario_name / "electricity_demand.csv"
        replace_symlink(output, scenario_link)
        print(f"{scenario_link} -> {output} ({len(yearly)} rows)")

    combined = demand[demand.index.year.isin(years)]
    combined_output = prepared_dir / (
        f"electricity_demand_{args.start_year}_{args.end_year}_no_leap.csv"
    )
    combined.to_csv(combined_output, index_label=demand.index.name)
    replace_symlink(combined_output, resources_dir / "electricity_demand.csv")
    print(f"{resources_dir / 'electricity_demand.csv'} -> {combined_output}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
