import pypsa

import pandas as pd
import geopandas as gpd
import matplotlib.pyplot as plt

# 1. 路径配置
geojson_path = "/gpfs1/data/compoundx/yumeng/energy_modellingtest/updated/extracted_nc_files2/shpfiles/gdf_128_updated.geojson"
solar_path = "/gpfs1/data/compoundx/yumeng/energy_modellingtest/updated/extracted_nc_files2/repreprocess/128updated/revised/2021ic/solarhourly_19412023.csv"
wind_path = "/gpfs1/data/compoundx/yumeng/energy_modellingtest/updated/extracted_nc_files2/repreprocess/128updated/revised/2021ic/onwindhourly_19412023.csv"

# 2. 建立映射：找到所有属于德国 (DE) 的数字 ID
gdf = gpd.read_file(geojson_path)
# 提取 new_name 以 'DE' 开头的行的 'name' 字段
# 注意：强制转为 str，确保与 CSV 表头匹配
de_numeric_ids = gdf[gdf['new_name'].str.startswith('DE')]['name'].astype(str).tolist()

print(f"✅ 找到德国区域对应的数字代码共 {len(de_numeric_ids)} 个")

# 3. 定义分块读取函数（带列过滤）
def get_jan_2015_german_data(file_path, target_ids):
    jan_data = []
    chunksize = 100000 
    
    print(f"正在精准扫描文件: {file_path.split('/')[-1]} ...")
    
    # 第一次读一行，确定哪些 ID 确实存在于这个 CSV 中
    header = pd.read_csv(file_path, nrows=0).columns
    valid_cols = [c for c in target_ids if c in header]
    

    for chunk in pd.read_csv(file_path, index_col=0, parse_dates=True, chunksize=chunksize):
        # 时间筛选
        matched = chunk.loc["2015-01-01":"2015-01-31"]
        if not matched.empty:
            # 只提取属于德国的列
            jan_data.append(matched[valid_cols])
            
            if chunk.index[-1] > pd.Timestamp("2015-01-31"):
                break
                
    return pd.concat(jan_data).sum(axis=1)

# 4. 提取数据
solar_de_jan = get_jan_2015_german_data(solar_path, de_numeric_ids)
wind_de_jan = get_jan_2015_german_data(wind_path, de_numeric_ids)

# 5. 绘图
print("正在生成德国 1 月份电力潜力图...")
fig, ax1 = plt.subplots(figsize=(16, 7))

# 左轴：发电潜力
ax1.plot(solar_de_jan, label="Germany Solar Potential", color="#f9d002", lw=2)
ax1.plot(wind_de_jan, label="Germany Onwind Potential", color="#235ebc", lw=2)
ax1.set_ylabel("Generation Potential [MW]", fontsize=12)
ax1.set_xlabel("Time (January 2015)", fontsize=12)
ax1.legend(loc="upper left")
ax1.grid(True, alpha=0.3)
ax1.set_ylim(0, max(solar_de_jan.max(), wind_de_jan.max()) * 1.2)

plt.title("Germany: Validation of Solar & Wind (Jan 2015)", fontsize=14)
plt.tight_layout()
plt.savefig("/gpfs1/schlecker/home/mengyu/projects/pypsa-eur/check_process_folder/plots/DE_generation_josp.png", dpi=300)
plt.show()

# n = pypsa.Network("/gpfs1/schlecker/home/mengyu/projects/pypsa-eur/results/networks/base_s_64_elec_.nc")
# # 1. 筛选全欧洲 (所有 Bus) 的组件索引
# eu_solar_i = n.generators.query("carrier == 'solar'").index
# eu_onwind_i = n.generators.query("carrier == 'onwind'").index
# eu_load_i = n.loads.index  # 所有的负荷

# # 2. 计算实际发电潜力 (p_max_pu * p_nom)
# solar_potential_eu = (n.generators_t.p_max_pu[eu_solar_i] * n.generators.loc[eu_solar_i, "p_nom"]).sum(axis=1)
# onwind_potential_eu = (n.generators_t.p_max_pu[eu_onwind_i] * n.generators.loc[eu_onwind_i, "p_nom"]).sum(axis=1)

# # 负荷计算
# # 同样根据数据情况，确认是读取 .p 还是 .p_set
# load_col = "p" if not n.loads_t.p.empty else "p_set"
# total_load_eu = n.loads_t[load_col][eu_load_i].sum(axis=1)

# # 3. 绘图：双坐标轴
# fig, ax1 = plt.subplots(figsize=(15, 7))

# # 左轴 (ax1): 绘制全欧发电量潜力
# ax1.plot(solar_potential_eu, label="Europe Solar Potential", color="#f9d002", lw=2)
# ax1.plot(onwind_potential_eu, label="Europe Onwind Potential", color="#235ebc", lw=2)
# ax1.set_ylabel("Generation Potential [MW]", fontsize=12)
# ax1.set_xlabel("Time (Jan 2015)", fontsize=12)
# ax1.legend(loc="upper left")
# ax1.grid(True, alpha=0.3)

# # 右轴 (ax2): 绘制全欧负荷
# ax2 = ax1.twinx()
# ax2.plot(total_load_eu, label="Total Europe Load", color="#d62728", linestyle="--", alpha=0.8)
# ax2.set_ylabel("Demand / Load [MW]", fontsize=12, color="#d62728")
# ax2.tick_params(axis='y', labelcolor="#d62728")
# ax2.legend(loc="upper right")

# plt.title("Europe: Potential Generation (Jan 2015, 64 Clusters)")
# plt.tight_layout()
# plt.savefig("/gpfs1/schlecker/home/mengyu/projects/pypsa-eur/check_process_folder/plots/europe_generation_load.png", dpi=300)
# plt.show()