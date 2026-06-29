import pypsa
import pandas as pd
import geopandas as gpd
import matplotlib.pyplot as plt
import seaborn as sns

# --- 1. 路径配置 ---
geojson_path = "/gpfs1/data/compoundx/yumeng/energy_modellingtest/updated/extracted_nc_files2/shpfiles/gdf_128_updated.geojson"
onwind_ic_path = "/gpfs1/data/compoundx/yumeng/energy_modellingtest/updated/extracted_nc_files2/repreprocess/128updated/revised/onwindic.csv"
net_path = "/gpfs1/data/compoundx/yumeng/paper2/pypsa_output/networks/base_s_512_elec_.nc"
net_path1 = "/gpfs1/data/compoundx/yumeng/paper2/pypsa_output/warming2_s0_weather_year_2015/networks/base_s_512_elec_.nc"
# --- 2. 获取德国 ID 映射 ---
gdf = gpd.read_file(geojson_path)
# 假设 name 列是数字 ID，new_name 包含国家前缀 'DE'
de_ids = gdf[gdf['new_name'].str.startswith('DE', na=False)]['name'].astype(str).tolist()
print(f"✅ 识别到德国节点 ID 数量: {len(de_ids)}")

# --- 3. 处理 第一部分：onwindic.csv (2015年) ---
df_ic = pd.read_csv(onwind_ic_path, index_col=0)

de_rows_csv = [idx for idx in df_ic.index if str(idx).split(' ')[0] in de_ids]
df_de_csv = df_ic.loc[de_rows_csv]

# 提取 2015 列 (直接使用 '2015'，如果报错请改为 str(2015) 或 '2015.0')
try:
    csv_2015_values = df_de_csv['2015']
except KeyError:
    # 自动兼容带小数点的列名如 '2015.0'
    col_name = [c for c in df_de_csv.columns if '2015' in str(c)][0]
    csv_2015_values = df_de_csv[col_name]

print(f"✅ CSV 提取完成。德国 2015 总装机: {csv_2015_values.sum() / 1e3:.2f} GW")

# --- 4. 处理 第二部分：PyPSA Network (base_s_512) ---
n = pypsa.Network(net_path)
# 筛选德国节点上的陆上风电
de_buses = n.buses[n.buses.index.str.contains("DE", na=False)].index
de_gens = n.generators[(n.generators.bus.isin(de_buses)) & (n.generators.carrier == "onwind")]
net_values = de_gens['p_nom'] 
print(f"✅ Network 提取完成。模型总装机: {net_values.sum() / 1e3:.2f} GW")


n1 = pypsa.Network(net_path1)
# 筛选德国节点上的陆上风电
de_buses1 = n1.buses[n1.buses.index.str.contains("DE", na=False)].index
de_gens1 = n1.generators[(n1.generators.bus.isin(de_buses1)) & (n1.generators.carrier == "onwind")]
net_values1 = de_gens1['p_nom'] 
print(f"✅ Network 提取完成。模型总装机: {net_values1.sum() / 1e3:.2f} GW")
 # 筛选德国的生成器，查看其是否可扩展（即容量是否由模型优化决定）
# de_gens_status = n.generators.loc[
#     n.generators.bus.str.contains("DE"), 
#     ["carrier", "p_nom", "p_nom_min", "p_nom_max", "p_nom_extendable"]
# ]

# # 查看前几行
# print(de_gens_status.head())
# # 统计每种技术有多少个节点开启了扩展选项
# print("\n--- 各技术类型的可扩展性统计 ---")
# print(de_gens_status.groupby("carrier")["p_nom_extendable"].value_counts())

# # --- 5. 绘图：Boxplot 对比 ---
# # 准备绘图数据
# data_to_plot = pd.concat([
#     pd.DataFrame({'Capacity (MW)': csv_2015_values.values, 'Type': 'CSV Static (2015)'}),
#     pd.DataFrame({'Capacity (MW)': net_values.values, 'Type': 'Network Base (p_nom)'})
# ])

# plt.figure(figsize=(8, 6))
# sns.set_context("notebook", font_scale=1.2)
# sns.set_style("whitegrid")

# # 绘制 Boxplot
# sns.boxplot(x='Type', y='Capacity (MW)', data=data_to_plot, palette="Set3", showmeans=True)
# # 叠加抖动散点以查看具体分布情况
# sns.stripplot(x='Type', y='Capacity (MW)', data=data_to_plot, color=".3", alpha=0.4)

# plt.title("Comparison of Onwind Installed Capacity (Germany)", fontsize=14)
# plt.ylabel("Installed Capacity [MW]")
# plt.xlabel("Data Source")

# plt.tight_layout()
# plt.savefig("/gpfs1/data/compoundx/yumeng/project_code/pypsa-eur/check_process_folder/plots/DE_onwind_capacity_comparison.png", dpi=150)
# plt.show()

