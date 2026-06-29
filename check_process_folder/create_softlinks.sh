#!/bin/bash
SOURCE_ROOT="/gpfs1/data/compoundx/yumeng/paper2/atlite/cutouts"
TARGET_DIR="/gpfs1/data/compoundx/yumeng/project_code/pypsa-eur/data/cutout/build/unknown"

# 确保目标目录存在
mkdir -p "$TARGET_DIR"


# 循环 Warming Levels (2, 3, 4)
for wl in 2 3 4; do
    # 循环年份 (2015-2024)
    for yr in {2015..2024}; do
        
        # 1. 构造原始文件的绝对路径
        SRC_FILE="${SOURCE_ROOT}/warming${wl}/mme_results/hybrid_cutout_${yr}.nc"
        
        # 2. 构造软链接的文件名 (必须与 scenario.yaml 中的 default_cutout 匹配)
        # 匹配格式: my-hybrid-warming{wl}-{yr}.nc
        LINK_NAME="my-hybrid-warming${wl}-${yr}.nc"
        
        # 3. 执行建立软链接 (使用 -sf 强制覆盖已存在的链接)
        if [ -f "$SRC_FILE" ]; then
            ln -sf "$SRC_FILE" "${TARGET_DIR}/${LINK_NAME}"
            echo "✅ 已链接: warming${wl} 年份 ${yr} -> ${LINK_NAME}"
        else
            echo "⚠️ 警告: 未找到源文件 ${SRC_FILE}"
        fi
    done
done

echo "🎉 所有软链接建立完成！"