import pypsa
import xarray as xr
import pandas as pd
from pathlib import Path

# 设置路径
base_path = Path("/home/mengyu/projects/pypsa-eur/results/networks/")
network_file = base_path / "base_s_64_elec_.nc"

# --- 方法 A: 使用 PyPSA 加载（推荐，查看电力系统逻辑） ---
n = pypsa.Network(str(network_file))

print("【系统概览】")
print(n) # 显示有多少个 Bus, Generator, Line 等

# 检查你关心的发电机出力 (Generator dispatch)
if not n.generators_t.p.empty:
    print("\n【发电机出力数据摘要】")
    print(n.generators_t.p.head())

unique_carriers = n.generators.carrier.unique()
print("【模型中包含的唯一发电技术成分】")
print(unique_carriers)

# 检查是否发生了扩建 (p_nom_opt vs p_nom)
print("\n【扩建结果检查】")
expansion = n.generators[['p_nom', 'p_nom_opt']]
print(expansion[expansion['p_nom_opt'] > expansion['p_nom']])

# # --- 方法 B: 使用 xarray 直接查看底层存储（查看所有变量名） ---
# ds = xr.open_dataset(network_file)
# print("\n【底层 NetCDF 变量列表】")
# print(list(ds.data_vars))

# 查看storage 
print("--- 1. 检查 Storage Units (通常包含 PHS 和 Hydro) ---")
if not n.storage_units.empty:
    print("包含的技术:", n.storage_units.carrier.unique())
    print(n.storage_units[['carrier', 'p_nom', 'p_nom_opt']].head())
else:
    print("Storage Units 表为空。")

print("\n--- 2. 检查 Stores (通常包含 Battery 和 H2) ---")
if not n.stores.empty:
    print("包含的技术:", n.stores.carrier.unique())
    # 注意：Store 的容量单位通常是 e_nom (能量) 而非 p_nom (功率)
    print(n.stores[['carrier', 'e_nom', 'e_nom_opt']].head())
else:
    print("Stores 表为空。")

print("\n--- 3. 检查 Generators 中的 Hydro (如 ror 径流式) ---")
hydro_in_gen = n.generators[n.generators.carrier.isin(['hydro', 'ror'])]
if not hydro_in_gen.empty:
    print(hydro_in_gen[['carrier', 'p_nom', 'p_nom_opt']])
else:
    print("发电机表中未发现水电成分。")