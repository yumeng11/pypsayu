# 10-year PyPSA-Eur warming run

This note documents the custom 10-year workflow used for the warming demand
experiments. It is meant as the small README to share together with the custom
run files.

## Files to share

- `sbatch_runpypsa_10y.sh`: Slurm entry point. It prepares links/data and then
  launches Snakemake for all 10 yearly targets.
- `setup_cutout_symlinks_warming3.sh`: links one weather cutout per year into
  the location where PyPSA-Eur expects cutout files.
- `prepare_demand_by_year_warming3.py`: splits one multi-year demand CSV into
  per-year demand CSVs and links each one into the matching scenario resource
  folder.
- `config/my_config3_10y.yaml`: main custom PyPSA-Eur config for this run.
- `config/scenario3_10y.yaml`: scenario definitions for weather years
  2015-2024.

Current repository path:

```text
/gpfs1/data/compoundx/yumeng/project_code/pypsa-eur
```

## What this run does

The run solves 10 weather-year cases, 2015 through 2024. Each case has the same
basic PyPSA-Eur configuration, but uses a different weather cutout and the
matching demand year.

For each year, the scenario name connects several files and folders:

```text
warming3_s0_weather_year_2015
warming3_s0_weather_year_2016
...
warming3_s0_weather_year_2024
```

That same scenario prefix is used in:

- `config/scenario3_10y.yaml`: the scenario block name.
- `prepare_demand_by_year_warming3.py`: `SCENARIO_PREFIX`.
- `resources/<scenario_name>/electricity_demand.csv`: the per-scenario demand
  symlink created by the Python helper.
- `sbatch_runpypsa_10y.sh`: output target folders under `OUTPUT_DIR`.

If the scenario name changes, update all of those places together.

## Current input data

Demand CSV:

```text
/gpfs1/data/compoundx/yumeng/paper2/pypsa_input_ready/warming3/mme_results/load_S0_warming3_GBupdated.csv
```

Weather cutout source folder:

```text
/gpfs1/data/compoundx/yumeng/paper2/atlite/cutouts/warming3/mme_results
```

Expected cutout filenames:

```text
hybrid_cutout_2015.nc
hybrid_cutout_2016.nc
...
hybrid_cutout_2024.nc
```

The scenario file refers to these cutouts as:

```text
my-hybrid-2015
my-hybrid-2016
...
my-hybrid-2024
```

so the symlink helper creates links named:

```text
my-hybrid-2015.nc
my-hybrid-2016.nc
...
my-hybrid-2024.nc
```

## Switching demand data

When using a new demand dataset, change the demand path in two places:

1. In `sbatch_runpypsa_10y.sh`, update:

```bash
DEMAND_FILE="/path/to/new/load.csv"
```

2. In `config/my_config3_10y.yaml`, update `load.custom_path` for
   traceability:

```yaml
load:
  prebuilt: true
  custom_path: "/path/to/new/load.csv"
```

The Python helper expects:

- first CSV column is timestamps;
- remaining columns are demand series expected by PyPSA-Eur;
- hourly data for every year in `YEARS = range(2015, 2025)`;
- leap day can be present, but it will be dropped.

The helper writes:

```text
resources/_prepared_demand/warming3_s0/electricity_demand_2015.csv
...
resources/_prepared_demand/warming3_s0/electricity_demand_2024.csv
resources/_prepared_demand/warming3_s0/electricity_demand_2015_2024_no_leap.csv
```

and links each yearly file to:

```text
resources/warming3_s0_weather_year_<YEAR>/electricity_demand.csv
```

If you are changing from `warming3_s0` to another demand/scenario label, also
update:

- `SCENARIO_PREFIX` in `prepare_demand_by_year_warming3.py`;
- the scenario block names in `config/scenario3_10y.yaml`;
- the output target folders in `sbatch_runpypsa_10y.sh`;
- `run.name` in `config/my_config3_10y.yaml`.

## Switching weather cutouts

When using a new weather cutout dataset, update:

1. `SOURCE_DIR` in `setup_cutout_symlinks_warming3.sh`:

```bash
SOURCE_DIR="/path/to/new/cutout/folder"
```

2. The expected filename pattern if the new files are not named
   `hybrid_cutout_<YEAR>.nc`:

```bash
source_file="${SOURCE_DIR}/hybrid_cutout_${year}.nc"
```

3. The linked cutout name if you want a different PyPSA-Eur cutout name:

```bash
link_file="${LINK_DIR}/my-hybrid-${year}.nc"
```

4. The matching cutout names in `config/scenario3_10y.yaml`:

```yaml
atlite:
  default_cutout: my-hybrid-2015
  cutouts:
    my-hybrid-2015:
      module: era5
      x: [-22., 45.]
      y: [33., 72.]
      dx: 0.3
      dy: 0.3
      time: ['2015-01', '2015-12']
renewable:
  onwind:
    cutout: my-hybrid-2015
  offwind-ac:
    cutout: my-hybrid-2015
  offwind-dc:
    cutout: my-hybrid-2015
  solar:
    cutout: my-hybrid-2015
```

Keep the `default_cutout`, the `atlite.cutouts` key, the renewable cutout names,
and the symlink filename consistent. If the symlink is `my-hybrid-2015.nc`, the
scenario should refer to `my-hybrid-2015`.

Also check that the cutout folder used by PyPSA-Eur is the same folder where the
symlinks are created. The two relevant settings are:

- `LINK_DIR` in `setup_cutout_symlinks_warming3.sh`;
- `data.cutout.folder` in `config/my_config3_10y.yaml`.

If they differ, make them consistent before submitting the job.

## Running

From the repository root:

```bash
sbatch sbatch_runpypsa_10y.sh
```

The sbatch script will:

1. activate the `pypsa-eur-v2` conda environment;
2. create/log required folders;
3. link weather cutouts;
4. split and link demand data;
5. build the 10 Snakemake targets:

```text
/gpfs1/data/compoundx/yumeng/paper2/pypsa_output/warming3_s0_weather_year_2015/networks/base_s_128_elec_.nc
...
/gpfs1/data/compoundx/yumeng/paper2/pypsa_output/warming3_s0_weather_year_2024/networks/base_s_128_elec_.nc
```

## Quick checklist before submitting

- `PYPSA_DIR` points to the current repository.
- `DEMAND_FILE` exists and covers 2015-2024 hourly timestamps.
- `SOURCE_DIR` contains one cutout file per year.
- `LINK_DIR` matches `data.cutout.folder` or both point to the cutout location
  PyPSA-Eur should use.
- Scenario names in `scenario3_10y.yaml` match the output target names.
- `SCENARIO_PREFIX` in `prepare_demand_by_year_warming3.py` matches the
  scenario names.
- `bash -n sbatch_runpypsa_10y.sh` passes before submitting.
