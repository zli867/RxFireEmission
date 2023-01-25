import pandas as pd
from shapely import geometry
from util import GeoHelper
import numpy as np
from datetime import datetime

"""
Add latitude and longitude if there is no such information in original permits
If the latitude and longitude is not in Georgia or if there is no such information,
delete and put it in invalid address file
"""

converted_address_list = "/Users/zongrunli/Desktop/SEEmission/ExtractPermitData/GA/Result/Valid_address_bing.csv"
permit_address = "/Users/zongrunli/Desktop/SEEmission/ExtractPermitData/GA/Result/Converted_Address.csv"
permit_data = "/Users/zongrunli/Desktop/SEEmission/ExtractPermitData/GA/Result/CombinedGA.csv"

res = pd.DataFrame(columns=('Id', 'State', 'Time', 'Lat', 'Lon', 'Burned_Area', 'BurnAddress'))

# combine address list
permit_address_df = pd.read_csv(permit_address)
permit_converted_df = pd.read_csv(converted_address_list)
permit_converted_df = permit_converted_df[["BurnAddress", "Lat", "Lon"]]
permit_all_address_df = pd.concat([permit_address_df, permit_converted_df])
permit_all_address_df = permit_all_address_df.reset_index(drop=True)
print(permit_all_address_df)

permit_data_df = pd.read_csv(permit_data)


# Fill the lat and lon for invalid_permit_df
temp_res = permit_data_df.merge(permit_all_address_df, how='left', on='BurnAddress')
# convert time to yyy-mm-dd
time_res = temp_res["DateOfBurn"]
time_list = []
for i in range(0, len(time_res)):
    date_obj = datetime.strptime(time_res[i][0: 10], "%Y-%m-%d")
    time_str = datetime.strftime(date_obj, "%Y-%m-%d")
    time_list.append(time_str)

res["Id"] = temp_res["id"]
res["State"] = ["GA"] * len(temp_res)
res["Time"] = time_list
res["Lat"] = temp_res["Lat_y"]
res["Lon"] = temp_res["Lon_y"]
res["Burned_Area"] = temp_res["TOBAcres"]
res["BurnAddress"] = temp_res["BurnAddress"]


# Generate new id
new_id = []
original_id = res["Id"].to_numpy()
for i in range(0, len(original_id)):
    new_id.append("GA" + str(original_id[i]))

res["Id"] = new_id
valid_res = res.dropna()
invalid_res = res[res["Lat"].isna()]

# Check unique id
print(len(valid_res))
print(len(set(valid_res["Id"])))
print(len(invalid_res))
print(len(set(invalid_res["Id"])))
# Save results
valid_res.to_csv("/Users/zongrunli/Desktop/SEEmission/ExtractPermitData/GA/Result/GA_2015_2020_valid.csv", index=False)
invalid_res.to_csv("/Users/zongrunli/Desktop/SEEmission/ExtractPermitData/GA/Result/GA_2015_2020_invalid.csv", index=False)