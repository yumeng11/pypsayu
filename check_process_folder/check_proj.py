# import geopandas as gpd
# import rasterio

# # 检查矢量数据
# df = gpd.read_file("resources/country_shapes.geojson")
# print("Vector CRS:", df.crs)

# # 检查栅格数据
# with rasterio.open("data/corine/archive/v18_5/corine.tif") as src:
#     print("Raster CRS:", src.crs)


import os
import sys

# 1. 在任何 GIS 库加载前，硬编码路径
env_path = "/home/mengyu/.conda/envs/pypsa-eur-v2"
os.environ["PROJ_DATA"] = f"{env_path}/share/proj"
os.environ["GDAL_DATA"] = f"{env_path}/share/gdal"
os.environ["PROJ_LIB"] = f"{env_path}/share/proj"

import rasterio
import geopandas as gpd
from rasterio.crs import CRS

# 2. 检查逻辑
try:
    with rasterio.open("data/corine/archive/v18_5/corine.tif") as src:
        print("Detected CRS:", src.crs)
        if src.crs and src.crs.is_projected:
            print("Status: SUCCESS")
        else:
            # 如果还是识别不出，尝试用代码“强行解析”
            print("Status: Identifying manually...")
            # 这里的字符串是从你报错信息里提取的关键特征
            manual_crs = CRS.from_string("EPSG:3035") 
            print("Manual EPSG:3035 recognition:", manual_crs)
except Exception as e:
    print("Error:", e)