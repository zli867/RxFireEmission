import pandas as pd
import numpy as np

all_address = pd.read_csv("/Users/zongrunli/Desktop/SEEmission/ExtractPermitData/GA/Data/GA_BURN_ADDRESS_2.csv")
part_address = pd.read_csv("/Users/zongrunli/Desktop/SEEmission/ExtractPermitData/GA/Result/GA_Valid_address.csv")
all_address_list = list(all_address["BurnAddress"])
part_address_list = list(part_address["BurnAddress"])
print(len(set(all_address_list)))
print(len(set(part_address_list)))
left_address = list(set(all_address_list).difference(set(part_address_list)))
print(len(set(left_address)))
print(len(set(all_address_list).intersection(set(part_address_list))))
left_res = {}
left_res["BurnAddress"] = left_address
left_res["Lat"] = np.zeros(len(left_address))
left_res["Lat"][:] = np.nan
left_res["Lon"] = np.zeros(len(left_address))
left_res["Lon"][:] = np.nan

df = pd.DataFrame(left_res)
df.to_csv("left_address.csv", index=False)