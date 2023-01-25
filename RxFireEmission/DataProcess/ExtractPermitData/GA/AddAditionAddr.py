import pandas as pd
import matplotlib.pyplot as plt
from util import GeoHelper
from shapely import geometry
from ExtractHelper import convertAddressGoogle

valid_file = "/Users/zongrunli/Desktop/SEEmission/Data/Permits/GA Bing/GA_2015_2020_valid.csv"
addition_addr = "/Users/zongrunli/Desktop/SEEmission/Data/Permits/GA Bing/Addition_Addr.csv"

valid_df = pd.read_csv(valid_file)
addition_addr_df = pd.read_csv(addition_addr)
addr = addition_addr_df["BurnAddress"].to_numpy()
lat_add = addition_addr_df["Lat"].to_numpy()
lon_add = addition_addr_df["Lon"].to_numpy()
addr_dict = {}
for i in range(0, len(addr)):
    addr_dict[addr[i]] = [lat_add[i], lon_add[i]]

for index, row in valid_df.iterrows():
    if row["BurnAddress"] in addr_dict:
        valid_df.loc[index, "Lat"] = addr_dict[row["BurnAddress"]][0]
        valid_df.loc[index, "Lon"] = addr_dict[row["BurnAddress"]][1]
valid_df.to_csv("/Users/zongrunli/Desktop/SEEmission/Data/Permits/GA Bing/GA_2015_2020_valid_2.csv", index=False)

# state = GeoHelper.StatePolygon("Georgia")
# valid_df = pd.read_csv("/Users/zongrunli/Desktop/SEEmission/Data/Permits/GA Bing/GA_2015_2020_valid_2.csv")
# # invalid_addr = []
# # for index, row in valid_df.iterrows():
# #     fire_point = geometry.Point(row["Lon"], row["Lat"])
# #     if not state.contains(fire_point):
# #         invalid_addr.append(row["BurnAddress"])
# # invalid_addr = list(set(invalid_addr))
# # for i in range(0, len(invalid_addr)):
# #     # print(invalid_addr[i])
# #     lat, lng, addr_name = convertAddressGoogle(invalid_addr[i])
# #     print("{0},{1},{2},{3}".format(invalid_addr[i], lat, lng, addr_name))
#
#
# xs, ys = state.exterior.xy
# plt.plot(xs, ys, 'k')
# plt.scatter(valid_df["Lon"], valid_df["Lat"], s=1)
# plt.show()

