#!/bin/bash
#SBATCH --job-name=pypsa_test       
#SBATCH --nodes=1                     
#SBATCH --ntasks=1                   
#SBATCH --cpus-per-task=16            
#SBATCH --mem-per-cpu=20G             
#SBATCH --time=48:00:00              
#SBATCH -o /work/mengyu/job_log/%u/%x-%A.out
#SBATCH -e /work/mengyu/job_log/%u/%x-%A.err
#SBATCH --mail-type=END,FAIL
#SBATCH --mail-user=yu.meng@ufz.de


module purge
module load Conda/25.3.1
source activate pypsa-eur-v2

cd /gpfs1/data/compoundx/yumeng/project_code/pypsa-eur

mkdir -p logs

unset PROJ_LIB_DIR

ENV_PATH="/home/mengyu/.conda/envs/pypsa-eur-v2"

export PROJ_DATA="$ENV_PATH/share/proj"
export PROJ_LIB="$ENV_PATH/share/proj"
export GDAL_DATA="$ENV_PATH/share/gdal"


# TARGET="/gpfs1/data/compoundx/yumeng/paper2/pypsa_output/networks/base_s_64_elec_.nc"

# snakemake $TARGET \
#     --configfile /gpfs1/data/compoundx/yumeng/project_code/pypsa-eur/config/config.default.yaml \
#     --configfile /gpfs1/data/compoundx/yumeng/project_code/pypsa-eur/config/archive_single_year_runs/jan2015_cutout_test_config.yaml \
#     -j $SLURM_CPUS_PER_TASK \
#     --keep-going \
#     --rerun-incomplete \

# echo "Job finished at $(date)"

TARGET="/gpfs1/data/compoundx/yumeng/paper2/pypsa_output/warming2_s0_weather_year_2015_noclip/networks/base_s_64_elec_.nc"
snakemake $TARGET \
    --configfile /gpfs1/data/compoundx/yumeng/project_code/pypsa-eur/config/config.default.yaml \
    --configfile /gpfs1/data/compoundx/yumeng/project_code/pypsa-eur/config/archive_single_year_runs/warming2_s0_2015_noclip_config.yaml \
    --cores 32 \
    --keep-going \
    --rerun-incomplete \
    
echo "Job finished at $(date)"

# 多情景全部年份数据模型运行
# TARGETS=""
# for w in warming2 warming3 warming4; do
#     for d in S0 S1 S2 S3 S4 S5; do
#         for yr in {2015..2024}; do
#             TARGETS+="/gpfs1/data/compoundx/yumeng/paper2/pypsa_output/${w}_${d}_${yr}/networks/base_s_64_elec_.nc "
#         done
#     done
# done

# snakemake $TARGETS \
#     --configfile config/config.default.yaml \
#     --configfile config/config.warming.yaml \
#     -j 24 \
#     --keep-going