import ExtractHelper
import pandas as pd
import numpy as np

filename = "/Users/zongrunli/Desktop/SEEmission/ExtractPermitData/GA/Data/SplitAddr/split_8.csv"
df = pd.read_csv(filename)
df.insert(df.shape[1], 'Lat', np.NAN)
df.insert(df.shape[1], 'Lon', np.NAN)
address = df['BurnAddress']
lat_res = []
lon_res = []
start_idx = 0
try:
    for i in range(start_idx, len(address)):
        cur_address = address[i]
        cur_lat, cur_lng = ExtractHelper.convertAddressImproved(cur_address)
        lat_res.append(cur_lat)
        lon_res.append(cur_lng)
        # print(cur_lat)
        # if i >= 1:
        #     break
except:
    print("Error Happens")
    print(str(len(lat_res)) + " Addresses Converted.")
    df['Lat'][start_idx: start_idx + len(lat_res)] = lat_res
    df['Lon'][start_idx: start_idx + len(lat_res)] = lon_res
    df.to_csv("/Users/zongrunli/Desktop/SEEmission/ExtractPermitData/GA/Data/SplitAddr/Converted_Bing/split_8_tmp.csv",
              index=False)
else:
    df['Lat'] = lat_res
    df['Lon'] = lon_res
    df.to_csv("/Users/zongrunli/Desktop/SEEmission/ExtractPermitData/GA/Data/SplitAddr/Converted_Bing/split_8_converted.csv", index=False)