import pandas as pd
from datetime import datetime
import pickle

filename = "/Users/zongrunli/Desktop/SEEmission/ExtractPermitData/GA/Data/Combined/CombinedGA.csv"
df = pd.read_csv(filename)
burn_hour = []
burn_area = []
start_hour_arry = []
end_hour_arry = []


for index, row in df.iterrows():
    if pd.isna(row["BeginTime"]) or pd.isna(row["EndTime"]) or pd.isna(row["TOBAcres"]):
        continue
    start_hour = str(row["BeginTime"])
    end_hour = str(row["EndTime"])
    area = row["TOBAcres"]
    if area < 0 or len(start_hour) != 4 or len(end_hour) != 4 or start_hour == "2400" or end_hour=="2400":
        continue
    else:
        try:
            start_hour = datetime.strptime(start_hour, '%H%M')
            end_hour = datetime.strptime(end_hour, '%H%M')
            duration = end_hour - start_hour
            seconds = duration.total_seconds()
            hours = seconds / 3600
            burn_hour.append(hours)
            burn_area.append(area)
            start_hour_arry.append(start_hour)
            end_hour_arry.append(end_hour)
        except:
            print(index)

res_dict = {"area": burn_area, "duration_hour": burn_hour, "start_hour": start_hour_arry, "end_hour": end_hour_arry}
# save data if you want
with open('/Users/zongrunli/Desktop/SEEmission/Visualization/Figure data/duration_vs_area.pkl', 'wb') as handle:
    pickle.dump(res_dict, handle, protocol=pickle.HIGHEST_PROTOCOL)

