import ExtractHelper
import pandas as pd
import numpy as np

df = pd.read_csv("/Users/zongrunli/Desktop/SEEmission/ExtractPermitData/GA/Data/Combined/CombinedGA.csv")
df.insert(df.shape[1], 'Lat', np.NAN)
df.insert(df.shape[1], 'Lon', np.NAN)
address_list = []
already_converted_address = {}
# add the existed coordinates into dict
for idx, row in df.iterrows():
    address = df.iloc[idx].at["BurnAddress"]
    lat_deg = df.iloc[idx].at["LatDeg"]
    lat_min = df.iloc[idx].at["LatMin"]
    lat_sec = df.iloc[idx].at["LatSec"]
    lng_deg = df.iloc[idx].at["LonDeg"]
    lng_min = df.iloc[idx].at["LonMin"]
    lng_sec = df.iloc[idx].at["LonSec"]
    coord_origin = np.array([lat_deg, lat_min, lat_sec, lng_deg, lng_min, lng_sec])
    contain_nan = (True in np.isnan(coord_origin))
    if not contain_nan:
        lat = ExtractHelper.convertCoordToFloat(lat_deg, lat_min, lat_sec)
        long = ExtractHelper.convertCoordToFloat(lng_deg, lng_min, lng_sec)
        if long > 0:
            long = -1 * long
        df.loc[idx, 'Lat'] = lat
        df.loc[idx, 'Lon'] = long
        # add the address to map
        if address in already_converted_address.keys():
            continue
        else:
            already_converted_address[address] = [lat, long]
    else:
        address_list.append(address)

df.to_csv("CombinedGA.csv", index=False)

# The address has already converted
converted_list = []
converted_lat = []
converted_lon = []
for key in already_converted_address.keys():
    converted_list.append(key)
    converted_lat.append(already_converted_address[key][0])
    converted_lon.append(already_converted_address[key][1])

df_converted = {"BurnAddress": converted_list, "Lat": converted_lat, "Lon": converted_lon}
df_converted = pd.DataFrame(df_converted)
df_converted.to_csv("Converted_Address.csv", index=False)


# Unique address
address_list = list(set(address_list))
address_list_res = []
for i in range(0, len(address_list)):
    if address_list[i] in already_converted_address.keys():
        continue
    else:
        address_list_res.append(address_list[i])
df_address = pd.DataFrame(address_list_res, columns=["BurnAddress"])
df_address.to_csv("GA_BURN_ADDRESS.csv", index=False)

# Split Address
ExtractHelper.SplitCSV("/Users/zongrunli/Desktop/SEEmission/ExtractPermitData/GA/Data/SplitAddr/GA_BURN_ADDRESS.csv", 10000,
                       "/Users/zongrunli/Desktop/SEEmission/ExtractPermitData/GA/Data/SplitAddr/")