import pandas as pd
from datetime import datetime
from util import GeoHelper
from shapely import geometry

southeastern_states = ["Alabama", "Georgia", "Tennessee", "Florida", "Mississippi",
                       "North Carolina", "South Carolina", "Arkansas", "Louisiana",
                       "Kentucky", "Virginia", "West Virginia"]
state_abbr = ["AL", "GA", "TN", "FL", "MS",
              "NC", "SC", "AR", "LA",
              "KY", "VA", "WV"]
state_polygons = []
for state_name in southeastern_states:
    state_polygons.append(GeoHelper.StatePolygon(state_name))

filename = "/Users/zongrunli/Desktop/SEEmission/Data/Wildfires/INCI/INCI_Full_History.csv"
df = pd.read_csv(filename)
time_res = []
lat_res = []
lon_res = []
id_res = []
burned_area_res = []
state_res = []

for index, row in df.iterrows():
    if row["IncidentTypeCategory"] == "RX":
        continue
    else:
        lon = row["X"]
        lat = row["Y"]
        # whether in the interest place
        fire_point = geometry.Point(lon, lat)
        contain_flag = False
        time_flag = False
        contained_state = None
        for poly_idx in range(0, len(state_polygons)):
            if state_polygons[poly_idx].contains(fire_point):
                contain_flag = True
                contained_state = state_abbr[poly_idx]
                break
        time_str = row["FireDiscoveryDateTime"][0: 10]
        time_obj = datetime.strptime(time_str, "%Y/%m/%d")
        # whether at research time
        if time_obj >= datetime(2013, 1, 1, 0, 0) and time_obj < datetime(2021, 1, 1, 0, 0):
            time_flag = True
        if contain_flag and time_flag:
            burned_area = row["DailyAcres"]
            time_new_str = datetime.strftime(time_obj, '%Y-%m-%d')
            id_tmp = "WFIGSFL" + str(index).rjust(6, "0")
            lon_res.append(lon)
            lat_res.append(lat)
            id_res.append(id_tmp)
            time_res.append(time_new_str)
            burned_area_res.append(burned_area)
            state_res.append(contained_state)
# Lat,Lon,Burned_Area
res_dict = {"Id": id_res, "State": state_res, "Time": time_res, "Lat": lat_res, "Lon": lon_res,
            "Burned_Area": burned_area_res}
df_res = pd.DataFrame.from_dict(res_dict)
df_res.to_csv("/Users/zongrunli/Desktop/SEEmission/ExtractWildfires/WFIGS/Combined_INCI_wf.csv", index=False)