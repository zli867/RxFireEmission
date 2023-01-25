import os
import pandas as pd
from util import GeoHelper
from shapely import geometry
import numpy as np

# # Read converted data by using API
file_directory = "/Users/zongrunli/Desktop/SEEmission/ExtractPermitData/GA/Data/SplitAddr_Bing/Converted_Bing/"
# converted_address = []
# for filename in os.listdir(file_directory):
#     if ".csv" in filename:
#         df = pd.read_csv(file_directory + filename)
#         converted_address.append(df)
#
# # Combine all address
# converted_df = pd.concat(converted_address)
# converted_df = converted_df.reset_index(drop=True)

# Single file:
filename = "/Users/zongrunli/Desktop/SEEmission/ExtractPermitData/GA/Data/SplitAddr_Bing/Converted_Bing/invalid_bing_converted.csv"
converted_df = pd.read_csv(filename)

print("Total converted address: " + str(len(converted_df)))


# Delete the invalid address
invalid_address = []
# In Georgia or not and is Georgia or not (sometime just give georgia coordinate)
state_polygon = GeoHelper.StatePolygon("Georgia")
valid_idx = []
for index, row in converted_df.iterrows():
    lat = row['Lat']
    lon = row['Lon']
    fire_point = geometry.Point(lon, lat)
    if not state_polygon.contains(fire_point):
        converted_df.at[index, 'Lat'] = np.nan
        converted_df.at[index, 'Lon'] = np.nan
        invalid_address.append(converted_df.at[index, 'BurnAddress'])
    elif converted_df.at[index, 'Matched_Address'] == "Georgia":
        converted_df.at[index, 'Lat'] = np.nan
        converted_df.at[index, 'Lon'] = np.nan
        invalid_address.append(converted_df.at[index, 'BurnAddress'])
print("Invalid converted address: " + str(len(invalid_address)))
converted_df = converted_df.dropna(subset=['Lat', 'Lon'])
converted_df = converted_df.reset_index(drop=True)
print("Valid converted address: " + str(len(converted_df)))
invalid_df = pd.DataFrame.from_dict({"BurnAddress": invalid_address})

invalid_df.to_csv(file_directory + "Invalid_address_bing_final.csv", index=False)
converted_df.to_csv(file_directory + "Valid_address_bing_part.csv", index=False)
