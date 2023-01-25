import pandas as pd
from util import GeoHelper
from shapely import geometry
import numpy as np

filenames = ["/Users/zongrunli/Desktop/SEEmission/ExtractPermitData/GA/Temp Data/GA_Invalid_Address_converted.csv"]

permits_data = []

for filename in filenames:
    df = pd.read_csv(filename)
    permits_data.append(df)

res = pd.concat(permits_data)
# In Georgia or not
state_polygon = GeoHelper.StatePolygon("Georgia")
valid_idx = []
for index, row in res.iterrows():
    lat = row['Lat']
    lon = row['Lon']
    fire_point = geometry.Point(lon, lat)
    if not state_polygon.contains(fire_point):
        res.at[index, 'Lat'] = np.nan
        res.at[index, 'Lon'] = np.nan

res_nan = res[res['Lat'].isna()]

res_nan.to_csv("/Users/zongrunli/Desktop/SEEmission/ExtractPermitData/GA/Temp Data/GA_Invalid_test_4.csv", index=False)
res = res.dropna()
res.to_csv("/Users/zongrunli/Desktop/SEEmission/ExtractPermitData/GA/Temp Data/GA_valid_test_4.csv", index=False)
# res.to_csv("GA_addresses.csv", index=False)