#!/bin/bash
#SBATCH --job-name=pypsa_warming3_s0_10y
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=16
#SBATCH --mem-per-cpu=20G
#SBATCH --time=36:00:00
#SBATCH -o /work/mengyu/job_log/%u/%x-%A.out
#SBATCH -e /work/mengyu/job_log/%u/%x-%A.err
#SBATCH --mail-type=END,FAIL
#SBATCH --mail-user=yu.meng@ufz.de

set -euo pipefail

module purge
module load Conda/25.3.1
source activate pypsa-eur-v2

PYPSA_DIR="/gpfs1/data/compoundx/yumeng/project_code/pypsa-eur"
WORKFLOW_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
CONFIG_DIR="${PYPSA_DIR}/config"
RESOURCES_DIR="${PYPSA_DIR}/resources"
CUTOUTS_DIR="${PYPSA_DIR}/cutouts"
OUTPUT_DIR="/gpfs1/data/compoundx/yumeng/paper2/pypsa_output"
DEMAND_FILE="/gpfs1/data/compoundx/yumeng/paper2/pypsa_input_ready/warming3/mme_results/load_S0_warming3_GBupdated.csv"

cd "$PYPSA_DIR"
mkdir -p logs "$CONFIG_DIR" "$RESOURCES_DIR" "$CUTOUTS_DIR" "$OUTPUT_DIR"

unset PROJ_LIB_DIR

ENV_PATH="/home/mengyu/.conda/envs/pypsa-eur-v2"
export PROJ_DATA="$ENV_PATH/share/proj"
export PROJ_LIB="$ENV_PATH/share/proj"
export GDAL_DATA="$ENV_PATH/share/gdal"

echo "Job started at $(date)"
echo "CPUS=$SLURM_CPUS_PER_TASK"

bash "${PYPSA_DIR}/setup_cutout_symlinks_warming3.sh"

if [[ ! -f "${CONFIG_DIR}/scenario3_10y.yaml" ]]; then
    echo "Missing scenario file: ${CONFIG_DIR}/scenario3_10y.yaml" >&2
    exit 1
fi
if [[ ! -f "${CONFIG_DIR}/my_config3_10y.yaml" ]]; then
    echo "Missing config file: ${CONFIG_DIR}/my_config3_10y.yaml" >&2
    exit 1
fi

if [[ ! -f "$DEMAND_FILE" ]]; then
    echo "Missing demand file: $DEMAND_FILE" >&2
    exit 1
fi
python "${PYPSA_DIR}/prepare_demand_by_year_warming3.py" \
    "$DEMAND_FILE" \
    "${RESOURCES_DIR}/_prepared_demand/warming3_s0" \
    "$RESOURCES_DIR"

export OMP_NUM_THREADS=1
export OPENBLAS_NUM_THREADS=1
export MKL_NUM_THREADS=1
export NUMEXPR_NUM_THREADS=1

TARGETS=()
for year in {2015..2024}; do
    mkdir -p "${OUTPUT_DIR}/warming3_s0_weather_year_${year}/networks"
    TARGETS+=("${OUTPUT_DIR}/warming3_s0_weather_year_${year}/networks/base_s_128_elec_.nc")
done

snakemake "${TARGETS[@]}" \
    --configfile "${CONFIG_DIR}/config.default.yaml" \
    --configfile "${CONFIG_DIR}/my_config3_10y.yaml" \
    --cores "$SLURM_CPUS_PER_TASK" \
    --resources mem_mb=$((SLURM_CPUS_PER_TASK * 20000)) \
    --latency-wait 120 \
    --printshellcmds \
    --keep-going \
    --rerun-incomplete

echo "Job finished at $(date)"
