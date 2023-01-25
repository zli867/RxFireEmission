import pandas as pd
import matplotlib.pyplot as plt
from util import GeoHelper
from shapely import geometry

# extract valid permits for FL, SC and GA. Change the permit file and state name to clean.
permit_file = "/Users/zongrunli/Desktop/SEEmission/NLCD/ExtractedData/FL_2013_2021_permits.csv"
state_name = "Florida"
state = GeoHelper.StatePolygon(state_name)
valid_df = pd.read_csv(permit_file)

invalid_idx = []
# remove the fire out of the state
for index, row in valid_df.iterrows():
    fire_point = geometry.Point(row["Lon"], row["Lat"])
    if not state.contains(fire_point):
        invalid_idx.append(index)

print(str(len(invalid_idx)) + " Fires are out of state")
valid_df = valid_df.drop(invalid_idx)

invalid_burned_area = valid_df[valid_df["Burned_Area"] <= 0]
print(str(len(invalid_burned_area)) + " Fires are less than 0 acres")
valid_df = valid_df[valid_df["Burned_Area"] > 0]

if state.geom_type == "MultiPolygon":
    for geom in state.geoms:
        xs, ys = geom.exterior.xy
        plt.plot(xs, ys, 'k')
        plt.scatter(valid_df["Lon"], valid_df["Lat"], s=1)
else:
    xs, ys = state.exterior.xy
    plt.plot(xs, ys, 'k')
    plt.scatter(valid_df["Lon"], valid_df["Lat"], s=1)
plt.show()

# After this process, you can remove agricultural from permits by use burn type differentiation module
valid_df.to_csv("/Users/zongrunli/Desktop/SEEmission/Data/Permits/FL_2013_2021_permits.csv", index=False)