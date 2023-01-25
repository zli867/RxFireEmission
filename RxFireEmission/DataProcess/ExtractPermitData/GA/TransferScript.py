import pandas as pd
from datetime import datetime

filename = "/Users/zongrunli/Desktop/SEEmission/ExtractPermitData/GA/Result/GA_2015_2020.csv"
df = pd.read_csv(filename)
res_df = pd.DataFrame(columns=('Id', 'State', 'Time', 'Lat', 'Lon', 'Burned_Area', 'BurnAddress'))
lat_res = []
lon_res = []
time_res = []
burn_area_res = []
id_res = []
address = []
for idx, row in df.iterrows():
    time = row['DateOfBurn'][0: 10]
    lat = row['Lat']
    lon = row['Lon']
    burn_area = row['TOBAcres']
    id_cur = row['id']
    address_cur = row["BurnAddress"]
    date_obj = datetime.strptime(time, "%Y-%m-%d")
    date_str = datetime.strftime(date_obj, "%Y-%m-%d")
    lat_res.append(lat)
    lon_res.append(lon)
    burn_area_res.append(burn_area)
    time_res.append(date_str)
    id_res.append(id_cur)
    address.append(address_cur)
res_df['Lat'] = lat_res
res_df['Lon'] = lon_res
res_df['Burned_Area'] = burn_area_res
res_df['Time'] = time_res
res_df['State'] = ['GA'] * len(res_df)
res_df['Id'] = id_res
res_df["BurnAddress"] = address
# res_df = res_df.dropna()
res_df.to_csv("GA_2015_2020_test.csv", index=False)
