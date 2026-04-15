import yaml
import os

# 定义维度
warming_levels = ["warming2", "warming3", "warming4"]
demand_sets = ["S0", "S1", "S2", "S3", "S4", "S5"]
years = range(2015, 2025)

scenarios = {}

for w in warming_levels:
    for d in demand_sets:
        for yr in years:
            # 唯一 Key: 例如 warming2_S0_2015
            key = f"{w}_{d}_{yr}"
            
            # 唯一气象名: 例如 my-hybrid-warming2-2015
            # 这样即便同一年份，不同 Warming Level 也会读不同的文件
            cutout_name = f"my-hybrid-{w}-{yr}"
            
            scenarios[key] = {
                "snapshots": {
                    "start": f"{yr}-01-01 00:00",
                    "end": f"{yr}-12-31 23:00",
                    "inclusive": "left"
                },
                "load": {
                    "custom_path": f"/gpfs1/data/compoundx/yumeng/paper2/pypsa_input_ready/{w}/mme_results/load_{d}_{w}.csv"
                },
                "atlite": {
                    "default_cutout": cutout_name #
                }
            }

# 确保 config 目录存在并写入
os.makedirs("config", exist_ok=True)
file_path = "config/scenario.warming.yaml"

try:
    with open(file_path, "w") as f:
        yaml.dump(scenarios, f, default_flow_style=False)
    print(f"✅ 成功！已生成 {len(scenarios)} 个场景配置。")
except Exception as e:
    print(f"❌ 写入失败: {e}")
    print(f"❌ 写入失败，错误原因: {e}")