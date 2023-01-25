import pandas as pd
from shapely import geometry
from util import GeoHelper

"""
If the lat and long provide by the original permit data, use it. If not, use the geocoding result
Generate address list for generating the final permit data
"""

address_list = "/Users/zongrunli/Desktop/SEEmission/ExtractPermitData/GA/Result/AddressList.csv"
permits = "/Users/zongrunli/Desktop/SEEmission/ExtractPermitData/GA/Result/GA_2015_2020.csv"

address_list_df = pd.read_csv(address_list)
permits_df = pd.read_csv(permits)

all_address = list(set(permits_df["BurnAddress"]))
address_list_address = list(set(address_list_df["BurnAddress"]))

# Generate address from permits
permits_address_df = permits_df[["BurnAddress", "Lat", "Lon"]].dropna()
permits_address_df = permits_address_df.drop_duplicates()
permits_address_df = permits_address_df.reset_index(drop=True)

address_dict = {}
# Permits data
for idx, row in permits_address_df.iterrows():
    if row["BurnAddress"] in address_dict.keys():
        # print(address_dict[row["BurnAddress"]])
        # print([row["Lat"], row["Lon"]])
        # print("*" * 20)
        continue
    else:
        address_dict[row["BurnAddress"]] = [row["Lat"], row["Lon"]]

# Address list
for idx, row in address_list_df.iterrows():
    if row["BurnAddress"] in address_dict.keys():
        # print(address_dict[row["BurnAddress"]])
        # print([row["Lat"], row["Lon"]])
        # print("*" * 20)
        continue
    else:
        address_dict[row["BurnAddress"]] = [row["Lat"], row["Lon"]]

# Generate Final address list
state_polygon = GeoHelper.StatePolygon("Georgia")
res_df = pd.DataFrame(columns=('BurnAddress', 'Lat', 'Lon'))
valid_address = []
valid_lat = []
valid_lon = []
for key in address_dict.keys():
    lat, lon = address_dict[key]
    fire_point = geometry.Point(lon, lat)
    if state_polygon.contains(fire_point):
        valid_address.append(key)
        valid_lat.append(lat)
        valid_lon.append(lon)
res_df["BurnAddress"] = valid_address
res_df["Lat"] = valid_lat
res_df["Lon"] = valid_lon
res_df.to_csv("Final_address_list.csv", index=False)




# permit_valid = permits_df.copy().dropna()
# permit_valid_address = list(set(permit_valid["BurnAddress"]))
#
# result_df = pd.DataFrame(columns=('BurnAddress', 'Lat', 'Lon'))
# result_df["BurnAddress"] = all_address
