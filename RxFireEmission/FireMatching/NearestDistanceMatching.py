import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime
from MatchingHelper import distanceMapping
import pickle
from sklearn.linear_model import LinearRegression

# load data
permits_filename = "/Volumes/SERDP Modeling/RxEmissionData/permits/GA_2015_2020_permits_rx.csv"
finn_filename = "/Volumes/SERDP Modeling/RxEmissionData/FINN/Rx/GA_Combined_MODIS_VIIRS_rx.csv"
dateparse = lambda x: datetime.strptime(x, '%Y-%m-%d')
permits = pd.read_csv(permits_filename, parse_dates=['Time'], date_parser=dateparse)
finn = pd.read_csv(finn_filename, parse_dates=['DAY'], date_parser=dateparse)

combined_df = distanceMapping(finn, permits)

step = 100
r2_results = []
distance_res = []
for distance in range(500, 3000 + step, step):
    select_df = combined_df[combined_df["Dist"] <= distance]
    x = select_df["AREA"].to_numpy().reshape(-1, 1)
    y = select_df["Burned_Area"].to_numpy().reshape(-1, 1)
    reg = LinearRegression(fit_intercept=True).fit(x, y)
    r2_results.append(reg.score(x, y))
    distance_res.append(distance)

plt.plot(distance_res, r2_results)
plt.show()

res_dict = {"distance": distance_res, "r2": r2_results, "state": "GA"}
# save data if you want
with open('/Users/zongrunli/Desktop/SEEmission/Visualization/Figure data/ga_vanilla_dist_match.pkl', 'wb') as handle:
    pickle.dump(res_dict, handle, protocol=pickle.HIGHEST_PROTOCOL)