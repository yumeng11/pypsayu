#!/bin/bash
#SBATCH --job-name=pypsa_histcap2024_era5_dispatch
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=20
#SBATCH --mem-per-cpu=20G
#SBATCH --time=72:00:00
#SBATCH -o /work/mengyu/job_log/%u/%x-%A.out
#SBATCH -e /work/mengyu/job_log/%u/%x-%A.err
#SBATCH --mail-type=END,FAIL
#SBATCH --mail-user=yu.meng@ufz.de

set -euo pipefail

module purge
module load Conda/25.3.1
source activate pypsa-eur-v2

PYPSA_DIR="${PYPSA_DIR:-/gpfs1/data/compoundx/yumeng/project_code/pypsa-eur}"
WORKFLOW_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
CONFIG_DIR="${PYPSA_DIR}/config"
RESOURCES_DIR="${PYPSA_DIR}/resources"
CUTOUTS_DIR="${PYPSA_DIR}/data/cutout/build/unknown"
RESULTS_ROOT="${RESULTS_ROOT:-/gpfs1/data/compoundx/yumeng/paper2/pypsa_output}"
DEMAND_FILE="${DEMAND_FILE:-/gpfs1/data/compoundx/yumeng/paper2/pypsa_input_ready/historical_modelled_electricity_demand2015-2024.csv}"
CUTOUT_SOURCE_DIR="${CUTOUT_SOURCE_DIR:-/gpfs1/data/compoundx/yumeng/paper2/atlite/cutouts/his_era5}"

CONFIG_FILE_NAME="my_config_histcap2024_era5_dispatch_2015_2024.yaml"
SCENARIO_FILE_NAME="scenario_histcap2024_era5_dispatch_2015_2024.yaml"
SCENARIO_TEMPLATE="histcap2024_era5_weather_year_{year}"

START_YEAR="${START_YEAR:-2015}"
END_YEAR="${END_YEAR:-2024}"
CLUSTERS="${CLUSTERS:-128}"
OPTS="${OPTS:-}"

CONFIG_DEFAULT="${CONFIG_DEFAULT:-${CONFIG_DIR}/config.default.yaml}"
if [[ ! -f "$CONFIG_DEFAULT" && -f "${PYPSA_DIR}/config.default.yaml" ]]; then
    CONFIG_DEFAULT="${PYPSA_DIR}/config.default.yaml"
fi

cd "$PYPSA_DIR"
mkdir -p logs "$CONFIG_DIR" "$RESOURCES_DIR" "$CUTOUTS_DIR" "${RESULTS_ROOT%/}"

unset PROJ_LIB_DIR
ENV_PATH="${ENV_PATH:-/home/mengyu/.conda/envs/pypsa-eur-v2}"
export PROJ_DATA="$ENV_PATH/share/proj"
export PROJ_LIB="$ENV_PATH/share/proj"
export GDAL_DATA="$ENV_PATH/share/gdal"

export OMP_NUM_THREADS=1
export OPENBLAS_NUM_THREADS=1
export MKL_NUM_THREADS=1
export NUMEXPR_NUM_THREADS=1

echo "Job started at $(date)"
echo "PYPSA_DIR=$PYPSA_DIR"
echo "WORKFLOW_DIR=$WORKFLOW_DIR"
echo "CONFIG_DEFAULT=$CONFIG_DEFAULT"
echo "CUTOUTS_DIR=$CUTOUTS_DIR"
echo "CUTOUT_SOURCE_DIR=$CUTOUT_SOURCE_DIR"
echo "RESULTS_ROOT=${RESULTS_ROOT%/}"
echo "DEMAND_FILE=$DEMAND_FILE"
echo "CPUS=${SLURM_CPUS_PER_TASK:-1}"

if [[ ! -f "$CONFIG_DEFAULT" ]]; then
    echo "Missing default config: $CONFIG_DEFAULT" >&2
    exit 1
fi
if [[ ! -f "$DEMAND_FILE" ]]; then
    echo "Missing demand file: $DEMAND_FILE" >&2
    exit 1
fi
if [[ ! -d "$CUTOUT_SOURCE_DIR" ]]; then
    echo "Missing cutout source directory: $CUTOUT_SOURCE_DIR" >&2
    exit 1
fi

ln -sfn "${WORKFLOW_DIR}/${CONFIG_FILE_NAME}" "${CONFIG_DIR}/${CONFIG_FILE_NAME}"
ln -sfn "${WORKFLOW_DIR}/${SCENARIO_FILE_NAME}" "${CONFIG_DIR}/${SCENARIO_FILE_NAME}"

for year in $(seq "$START_YEAR" "$END_YEAR"); do
    source_cutout="${CUTOUT_SOURCE_DIR}/era5-${year}.nc"
    target_cutout="${CUTOUTS_DIR}/era5-${year}.nc"

    if [[ ! -f "$source_cutout" ]]; then
        echo "Missing ERA5 cutout for ${year}: $source_cutout" >&2
        exit 1
    fi

    ln -sfn "$source_cutout" "$target_cutout"
    echo "$target_cutout -> $source_cutout"
done

python "${WORKFLOW_DIR}/prepare_demand_by_year.py" \
    --source "$DEMAND_FILE" \
    --prepared-dir "${RESOURCES_DIR}/_prepared_demand/histcap2024_era5" \
    --resources-dir "$RESOURCES_DIR" \
    --scenario-template "$SCENARIO_TEMPLATE" \
    --start-year "$START_YEAR" \
    --end-year "$END_YEAR" \
    --drop-leap-day

solved_network_path() {
    local scenario="$1"
    printf "%s/%s/networks/base_s_%s_elec_%s.nc" \
        "${RESULTS_ROOT%/}" "$scenario" "$CLUSTERS" "$OPTS"
}

run_snakemake() {
    local target="$1"
    echo
    echo "Snakemake target: $target"
    snakemake "$target" \
        --configfile "$CONFIG_DEFAULT" \
        --configfile "${CONFIG_DIR}/${CONFIG_FILE_NAME}" \
        --cores "${SLURM_CPUS_PER_TASK:-1}" \
        --resources "mem_mb=$((${SLURM_CPUS_PER_TASK:-1} * 20000))" \
        --latency-wait 120 \
        --printshellcmds \
        --rerun-incomplete
}

echo
echo "Build each ERA5 weather-year network with 2024 historical capacities, then solve dispatch"
for year in $(seq "$START_YEAR" "$END_YEAR"); do
    scenario="${SCENARIO_TEMPLATE/\{year\}/$year}"
    solved_network="$(solved_network_path "$scenario")"

    echo
    echo "Weather year $year"
    echo "Solved dispatch network: $solved_network"

    run_snakemake "$solved_network"
done

echo "Job finished at $(date)"
