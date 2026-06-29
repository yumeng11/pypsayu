import pypsa
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
import cartopy.crs as ccrs
from sklearn.neighbors import NearestNeighbors

# ==========================================================
# 1. 路径与网络加载
# ==========================================================
path_clip = "/gpfs1/data/compoundx/yumeng/paper2/pypsa_output/warming2_s0_weather_year_2015_clip/networks/base_s_64_elec_.nc"
path_noclip = "/gpfs1/data/compoundx/yumeng/paper2/pypsa_output/warming2_s0_weather_year_2015_noclip/networks/base_s_64_elec_.nc"

n_clip = pypsa.Network(path_clip)
n_noclip = pypsa.Network(path_noclip)

def get_bus_xy(n):
    return n.buses[["x", "y"]].copy()

b1 = n_clip.buses.copy()
b2 = n_noclip.buses.copy()

gb1_clip = b1[b1.index.str.startswith("GB")]
gb1_noclip = b2[b2.index.str.startswith("GB")]

gb1 = b1[b1.index.str.startswith("GB")][["x", "y"]]
gb2 = b2[b2.index.str.startswith("GB")][["x", "y"]]
nn = NearestNeighbors(n_neighbors=1)

nn.fit(gb2[["x", "y"]])
dist, idx = nn.kneighbors(gb1[["x", "y"]])

mapping = pd.DataFrame({
    "clip_bus": gb1.index,
    "noclip_bus": gb2.index[idx.flatten()],
    "distance": dist.flatten()
})

print(mapping.sort_values("distance").head(20))
# print(n_clip.buses.columns)
# g1 = (
#     n_clip.generators
#     .loc[lambda df: df.bus.str.startswith("GB")]
#     .groupby("carrier")
#     .p_nom.sum()
# )

# g2 = (
#     n_noclip.generators
#     .loc[lambda df: df.bus.str.startswith("GB")]
#     .groupby("carrier")
#     .p_nom.sum()
# )

# diff = pd.concat(
#     [g1.rename("clip"),
#      g2.rename("noclip")],
#     axis=1
# )

# diff["delta"] = diff["noclip"] - diff["clip"]

# print(diff.sort_values("delta", key=np.abs, ascending=False))

# on1 = (
#     n_clip.generators
#     .query("carrier == 'solar'")
#     .groupby("bus")
#     .p_nom.sum()
# )

# on2 = (
#     n_noclip.generators
#     .query("carrier == 'solar'")
#     .groupby("bus")
#     .p_nom.sum()
# )

# diff = pd.concat(
#     [on1.rename("clip"),
#      on2.rename("noclip")],
#     axis=1
# ).fillna(0)

# diff["delta"] = diff["noclip"] - diff["clip"]

# print(
#     diff.loc[diff.index.str.startswith("GB")]
#         .sort_values("delta", key=np.abs, ascending=False)
#         .head(20)
# )