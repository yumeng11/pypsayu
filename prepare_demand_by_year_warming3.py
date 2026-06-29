#!/usr/bin/env python3
import os
import sys
from pathlib import Path

import pandas as pd


YEARS = range(2015, 2025)
SCENARIO_PREFIX = "warming3_s0_weather_year"


def read_demand(path):
    raw = pd.read_csv(path)
    if raw.empty:
        raise ValueError(f"Demand file is empty: {path}")

    time_col = raw.columns[0]
    timestamps = pd.to_datetime(raw[time_col], errors="coerce")
    if timestamps.isna().any():
        raise ValueError(
            "Could not parse the first CSV column as datetimes. "
            f"First column is: {time_col}"
        )

    data = raw.drop(columns=[time_col])
    index = pd.DatetimeIndex(timestamps)
    if index.tz is not None:
        index = index.tz_convert(None)
    data.index = index
    data.index.name = time_col
    return data


def expected_snapshots(year):
    snapshots = pd.date_range(
        f"{year}-01-01 00:00",
        f"{year}-12-31 23:00",
        freq="h",
    )
    return snapshots[~((snapshots.month == 2) & (snapshots.day == 29))]


def link_file(source, target):
    target.parent.mkdir(parents=True, exist_ok=True)
    if target.exists() or target.is_symlink():
        target.unlink()
    os.symlink(source, target)


def main():
    if len(sys.argv) != 4:
        print(
            "Usage: prepare_demand_by_year_warming3.py "
            "<source-demand.csv> <prepared-demand-dir> <pypsa-resources-dir>",
            file=sys.stderr,
        )
        return 2

    source_file = Path(sys.argv[1]).resolve()
    prepared_dir = Path(sys.argv[2]).resolve()
    resources_dir = Path(sys.argv[3]).resolve()

    if not source_file.is_file():
        raise FileNotFoundError(f"Missing demand file: {source_file}")

    prepared_dir.mkdir(parents=True, exist_ok=True)
    demand = read_demand(source_file)
    demand = demand[~((demand.index.month == 2) & (demand.index.day == 29))]

    for year in YEARS:
        expected = expected_snapshots(year)
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

        scenario_name = f"{SCENARIO_PREFIX}_{year}"
        scenario_link = resources_dir / scenario_name / "electricity_demand.csv"
        link_file(output, scenario_link)
        print(f"{scenario_link} -> {output} ({len(yearly)} rows)")

    combined_output = prepared_dir / "electricity_demand_2015_2024_no_leap.csv"
    combined = demand[demand.index.year.isin(YEARS)]
    combined.to_csv(combined_output, index_label=demand.index.name)
    link_file(combined_output, resources_dir / "electricity_demand.csv")
    print(f"{resources_dir / 'electricity_demand.csv'} -> {combined_output}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
