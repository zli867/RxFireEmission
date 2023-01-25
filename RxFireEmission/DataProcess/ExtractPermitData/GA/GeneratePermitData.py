import pandas as pd
from shapely import geometry
from util import GeoHelper
import numpy as np

"""
Add latitude and longitude if there is no such information in original permits
If the latitude and longitude is not in Georgia or if there is no such information,
delete and put it in invalid address file
"""
address_list = "/Users/zongrunli/Desktop/SEEmission/ExtractPermitData/GA/Result/Final_address_list.csv"
original_permits = "/Users/zongrunli/Desktop/SEEmission/ExtractPermitData/GA/Result/GA_2015_2020.csv"
invalid_permits = "/Users/zongrunli/Desktop/SEEmission/ExtractPermitData/GA/Result/unconverted.csv"

permits_df = pd.read_csv(original_permits)
address_list_df = pd.read_csv(address_list)

invalid_permit_df = permits_df[permits_df["Lat"].isna()]
valid_permit_df = permits_df.copy().dropna()

# Fill the lat and lon for invalid_permit_df
temp_res = invalid_permit_df.merge(address_list_df, how='left', on='BurnAddress')
res = pd.DataFrame(columns=('Id', 'State', 'Time', 'Lat', 'Lon', 'Burned_Area', 'BurnAddress'))
res["Id"] = temp_res["Id"]
res["State"] = temp_res["State"]
res["Time"] = temp_res["Time"]
res["Lat"] = temp_res["Lat_y"]
res["Lon"] = temp_res["Lon_y"]
res["Burned_Area"] = temp_res["Burned_Area"]
res["BurnAddress"] = temp_res["BurnAddress"]

res = res.append(valid_permit_df, ignore_index=True)
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