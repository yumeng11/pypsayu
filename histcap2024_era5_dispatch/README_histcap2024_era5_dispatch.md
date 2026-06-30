# 2024 Historical Capacity + ERA5 Dispatch Workflow

This workflow is for PyPSA-Eur `v2026.02.0`.

It does not edit `config.default.yaml`. The run uses:

```bash
snakemake <target> \
  --configfile config/config.default.yaml \
  --configfile config/my_config_histcap2024_era5_dispatch_2015_2024.yaml
```

## Files

- `my_config_histcap2024_era5_dispatch_2015_2024.yaml`
  - overlay config
  - sets 2024 historical capacities
  - disables capacity expansion through empty `extendable_carriers`
  - sets `transmission_limit: c1.0`
  - uses planning horizon and cost year `2024`

- `scenario_histcap2024_era5_dispatch_2015_2024.yaml`
  - ERA5 weather-year scenarios from 2015 to 2024
  - uses the same ERA5 domain and resolution as the existing ERA5 scenario config

- `prepare_demand_by_year.py`
  - splits a 2015-2024 hourly demand CSV into one file per year
  - links each file to `resources/<scenario>/electricity_demand.csv`

- `sbatch_histcap2024_era5_dispatch_2015_2024.sh`
  - runs the PyPSA-Eur native build + `solve_network` workflow on Slurm
  - links prebuilt ERA5 cutouts from
    `/gpfs1/data/compoundx/yumeng/paper2/atlite/cutouts/his_era5`
    to `PYPSA_DIR/data/cutout/build/unknown`

## Flow

```text
2015 ERA5 weather + 2024 historical capacities -> solve_network dispatch
2016 ERA5 weather + 2024 historical capacities -> solve_network dispatch
...
2024 ERA5 weather + 2024 historical capacities -> solve_network dispatch
```

Each weather-year scenario uses PyPSA-Eur's native profile/network-building rules.
The overlay config fixes the capacity year to 2024 and disables all capacity
expansion, so `solve_network` performs dispatch on a fixed-capacity network.

## Run

From the directory containing these workflow files:

```bash
sbatch sbatch_histcap2024_era5_dispatch_2015_2024.sh
```

The script defaults to:

```bash
PYPSA_DIR=/gpfs1/data/compoundx/yumeng/project_code/pypsa-eur
RESULTS_ROOT=/gpfs1/data/compoundx/yumeng/paper2/pypsa_output
DEMAND_FILE=/gpfs1/data/compoundx/yumeng/paper2/pypsa_input_ready/historical_modelled_electricity_demand2015-2024.csv
CUTOUT_SOURCE_DIR=/gpfs1/data/compoundx/yumeng/paper2/atlite/cutouts/his_era5
```

Before running Snakemake, the script creates links like:

```text
/gpfs1/data/compoundx/yumeng/project_code/pypsa-eur/cutouts/era5-2024.nc
  -> /gpfs1/data/compoundx/yumeng/paper2/atlite/cutouts/his_era5/era5-2024.nc
```

You can override them at submit time:

```bash
PYPSA_DIR=/gpfs1/data/compoundx/yumeng/project_code/pypsa-eur \
RESULTS_ROOT=/gpfs1/data/compoundx/yumeng/paper2/pypsa_output \
DEMAND_FILE=/path/to/demand_2015_2024.csv \
CUTOUT_SOURCE_DIR=/gpfs1/data/compoundx/yumeng/paper2/atlite/cutouts/his_era5 \
sbatch sbatch_histcap2024_era5_dispatch_2015_2024.sh
```

Solved networks are targeted at:

```text
/gpfs1/data/compoundx/yumeng/paper2/pypsa_output/histcap2024_era5_weather_year_<YEAR>/networks/base_s_128_elec_.nc
```

This is the `solve_network` output for an electricity-only PyPSA-Eur run with
empty `opts`.

## GitHub

Set the remote once:

```bash
git remote add origin git@github.com:yumeng11/pypsayu.git
```

If SSH is not configured on the cluster, use HTTPS instead:

```bash
git remote add origin https://github.com/yumeng11/pypsayu.git
```

Then push:

```bash
git add my_config_histcap2024_era5_dispatch_2015_2024.yaml \
        scenario_histcap2024_era5_dispatch_2015_2024.yaml \
        prepare_demand_by_year.py \
        sbatch_histcap2024_era5_dispatch_2015_2024.sh \
        README_histcap2024_era5_dispatch.md
git commit -m "Add 2024 capacity ERA5 dispatch workflow"
git branch -M main
git push -u origin main
```
