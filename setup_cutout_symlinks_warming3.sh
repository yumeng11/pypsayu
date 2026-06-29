#!/bin/bash
set -euo pipefail

SOURCE_DIR="/gpfs1/data/compoundx/yumeng/paper2/atlite/cutouts/warming3/mme_results"
LINK_DIR="/gpfs1/data/compoundx/yumeng/project_code/pypsa-eur/data/cutout/build/unknown"

mkdir -p "$LINK_DIR"

for year in {2015..2024}; do
    source_file="${SOURCE_DIR}/hybrid_cutout_${year}.nc"
    link_file="${LINK_DIR}/my-hybrid-${year}.nc"

    if [[ ! -f "$source_file" ]]; then
        echo "Missing cutout file: $source_file" >&2
        exit 1
    fi

    ln -sfn "$source_file" "$link_file"
    echo "$link_file -> $source_file"
done
