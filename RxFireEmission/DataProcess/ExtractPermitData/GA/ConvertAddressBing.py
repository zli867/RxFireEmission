import ExtractHelper
import pandas as pd
import numpy as np

filename = "/Users/zongrunli/Desktop/SEEmission/ExtractPermitData/GA/Data/SplitAddr_Bing/Converted_Bing/Invalid_address_bing.csv"
df = pd.read_csv(filename)
address = df['BurnAddress']
lat_res = []
lon_res = []
address_res = []
try:
    for i in range(0, len(address)):
        cur_address = address[i]
        cur_lat, cur_lng, found_address = ExtractHelper.convertAddressGoogle(cur_address)
        lat_res.append(cur_lat)
        lon_res.append(cur_lng)
        address_res.append(found_address)
        # print(cur_lat)
        # if i >= 1:
        #     break
except:
    print("Error Happens")
    print(str(len(lat_res)) + " Addresses Converted.")
    df['Lat'] = lat_res
    df['Lon'] = lon_res
    df['Matched_Address'] = address_res
    print(lat_res)
    print(lon_res)
    print(address_res)
    df.to_csv("/Users/zongrunli/Desktop/SEEmission/ExtractPermitData/GA/Data/SplitAddr_Bing/Converted_Bing/invalid_bing_tmp.csv",
              index=False)
else:
    df['Lat'] = lat_res
    df['Lon'] = lon_res
    df['Matched_Address'] = address_res
    df.to_csv("/Users/zongrunli/Desktop/SEEmission/ExtractPermitData/GA/Data/SplitAddr_Bing/Converted_Bing/invalid_bing_converted.csv",
              index=False)