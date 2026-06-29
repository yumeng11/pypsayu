import geopandas as gpd
import matplotlib.pyplot as plt
from shapely.geometry import box
import os

# 1. 设置路径 (确保这些文件在你运行脚本的目录下或路径正确)
regions_path = "resources/regions_offshore_base_s_1024.geojson"
background_path = "resources/country_shapes.geojson" # 使用项目自带的形状文件

# 你 config 里的 cutout 范围 [cite: 10]
cutout_x = [-12., 42.]
cutout_y = [33., 72.]

# 2. 加载数据
if not os.path.exists(regions_path):
    print(f"错误：找不到文件 {regions_path}")
    exit()

gdf = gpd.read_file(regions_path)
nl_target = gdf[gdf['name'] == 'NL2 29']

if nl_target.empty:
    print("错误：在 GeoJSON 中未找到 NL2 29。")
    print("当前文件中的前5个名称为:", gdf['name'].head().tolist())
    exit()

# 加载背景地图
if os.path.exists(background_path):
    europe = gpd.read_file(background_path)
else:
    print("警告：找不到 country_shapes.geojson，将只绘制区域和边界框。")
    europe = None

# 3. 创建 Cutout 的边界框 [cite: 10]
cutout_bounds = gpd.GeoDataFrame(
    {'geometry': [box(cutout_x[0], cutout_y[0], cutout_x[1], cutout_y[1])]}, 
    crs="EPSG:4326"
)

# 4. 开始绘图
fig, ax = plt.subplots(figsize=(12, 10))

if europe is not None:
    europe.plot(ax=ax, color='lightgrey', edgecolor='white', alpha=0.5)

# 绘制你定义的 Cutout 范围 (红框)
cutout_bounds.boundary.plot(ax=ax, color='red', linewidth=2, label='Cutout Box')

# 绘制 NL2 29 区域 (蓝色)
nl_target.plot(ax=ax, color='blue', edgecolor='black', alpha=0.8)

# 设置显示范围
ax.set_xlim(cutout_x[0] - 5, cutout_x[1] + 5)
ax.set_ylim(cutout_y[0] - 5, cutout_y[1] + 5)
ax.set_title("NL2 29 Location & Cutout Bounds Check", fontsize=15)
ax.grid(True, linestyle='--', alpha=0.6)

plt.legend(['Cutout Range', 'NL2 29 Area'])
plt.savefig("/gpfs1/data/compoundx/yumeng/project_code/pypsa-eur/check_process_folder/nl2_29_check_fixed.png")

# 5. 打印关键坐标对比
bounds = nl_target.total_bounds
print(f"\n--- 坐标检查 ---")
print(f"NL2 29 边界: 西:{bounds[0]:.2f}, 南:{bounds[1]:.2f}, 东:{bounds[2]:.2f}, 北:{bounds[3]:.2f}")
print(f"Cutout 边界: 西:{cutout_x[0]}, 南:{cutout_y[0]}, 东:{cutout_x[1]}, 北:{cutout_y[1]}")

if (bounds[0] > cutout_x[0] and bounds[2] < cutout_x[1] and 
    bounds[1] > cutout_y[0] and bounds[3] < cutout_y[1]):
    print("\n结论：该区域完全在 Cutout 范围内。")
else:
    print("\n结论：警告！该区域部分或全部超出了 Cutout 范围！")