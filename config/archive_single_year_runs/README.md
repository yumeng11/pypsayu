# Archived single-year run variants

These single-year test/run files were moved out of `config/` to keep the active
workflow files visible.

Active workflow files left in place:

- `../../sbatch_runpypsa_10y.sh`
- `../my_config3_10y.yaml`
- `../scenario3_10y.yaml`

Archived groups:

- `jan2015_cutout_test_config.yaml` +
  `jan2015_cutout_test_scenario.yaml`: January 2015 cutout/build test.
- `baseline_2015_config.yaml` + `baseline_2015_scenario.yaml` +
  `baseline_2015_sbatch.sh`: single-year baseline/prebuilt-load run.
- `warming2_s0_2015_noclip_config.yaml` +
  `warming2_s0_2015_noclip_scenario.yaml` +
  `warming2_s0_2015_noclip_sbatch.sh`: warming2 S0 2015 `noclip` run.
- `warming2_s0_2015_clip_config.yaml` +
  `warming2_s0_2015_clip_scenario.yaml` +
  `warming2_s0_2015_clip_sbatch.sh`: warming2 S0 2015 `clip` run.

The repository path is now:

`/gpfs1/data/compoundx/yumeng/project_code/pypsa-eur`

The archived launchers and configs have been updated to use this GPFS path and
to reference the matching archived config/scenario files in this folder.
