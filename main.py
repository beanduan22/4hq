import pandas as pd
import geopandas as gpd
from shapely.geometry import Point
import matplotlib.pyplot as plt
import numpy as np
# ============================
# 1. 读取 POI 数据
# ============================
df = pd.read_excel("主城2024_全属性_去重2.xlsx")   # 修改为你的文件名
# 列名请按你的数据修改：
lon_col = "经度"
lat_col = "纬度"
type_col = "平台化类型"
df = df.dropna(subset=[lon_col, lat_col])
# ============================
# 2. 转换为 GeoDataFrame
# ============================
gdf = gpd.GeoDataFrame(
    df,
    geometry=gpd.points_from_xy(df[lon_col], df[lat_col]),
    crs="EPSG:4326"
)
# ============================
# 3. 定义城市中心点（孙中山铜像）
# ============================
center_lon = 118.78407994987668
center_lat = 32.041834842438526
center = gpd.GeoDataFrame(
    geometry=[Point(center_lon, center_lat)],
    crs="EPSG:4326"
)
# ============================
# 4. 投影到米制坐标
# ============================
gdf = gdf.to_crs(epsg=3857)
center = center.to_crs(epsg=3857)
center_point = center.geometry.iloc[0]
# ============================
# 5. 计算距离（单位：米）
# ============================
gdf["distance"] = gdf.geometry.distance(center_point)
# ============================
# 6. 构建距离分段（每隔 600m）
# ============================
distance_bins = np.arange(0, 7500, 600)  # 0–7200 m，与示例一致
# 保存每一类的 CDF 数据
plot_data = {}
# ============================
# 7. 按平台化四类型分组计算 CDF
# ============================
types = sorted(gdf[type_col].unique())
for t in types:
    subset = gdf[gdf[type_col] == t].copy()
    subset = subset.sort_values("distance")
    counts = []
    for b in distance_bins:
        # 小于等于 b 的 POI 占比 (%)
        counts.append((subset["distance"] <= b).mean() * 100)
    plot_data[t] = counts
# ============================
# 8. 绘图
# ============================
plt.figure(figsize=(8, 5))
for t, vals in plot_data.items():
    plt.plot(distance_bins, vals, marker="o", label=f"类型 {t}")
plt.xlabel("距市中心的距离 (单位：m)")
plt.ylabel("%")
plt.ylim(0, 110)
plt.grid(True, linestyle="--", alpha=0.5)
plt.legend()
plt.title("平台化消费空间的距离累积分布")
plt.show()
