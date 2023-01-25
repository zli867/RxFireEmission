import pandas as pd
from MatchingHelper import relaxationDistDate
from datetime import datetime
from sklearn.linear_model import LinearRegression
from sklearn.metrics import r2_score
import statsmodels.api as sm
import pickle

fl_rec = "/Volumes/SERDP Modeling/RxEmissionData/permits/GA_2015_2020_permits_rx.csv"
fl_finn = "/Volumes/SERDP Modeling/RxEmissionData/FINN/Rx/GA_Combined_MODIS_VIIRS_rx.csv"
dateparse = lambda x: datetime.strptime(x, '%Y-%m-%d')
rec_df = pd.read_csv(fl_rec, parse_dates=['Time'], date_parser=dateparse)
finn_df = pd.read_csv(fl_finn, parse_dates=['DAY'], date_parser=dateparse)

# Hyper-parameters
area_lower_bound = 0

# Apply filter
finn_df = finn_df[finn_df["AREA"] >= area_lower_bound]
rec_df = rec_df[rec_df["Burned_Area"] >= area_lower_bound]

# Reset the index
finn_df = finn_df.reset_index(drop=True)
rec_df = rec_df.reset_index(drop=True)

step = 100
distance_array = []
r2_score_array = []
date_array = []
for day in range(0, 3):
    for distance in range(500, 3000 + step, step):
        res_df = relaxationDistDate(finn_df, rec_df, distance, day)
        X = res_df["AREA"].to_numpy().reshape(-1, 1)
        X_ = sm.add_constant(X)
        y = res_df["Burned_Area"].to_numpy().reshape(-1, 1)
        model = sm.OLS(y, X_)
        results = model.fit()
        r2 = results.rsquared
        distance_array.append(distance)
        date_array.append(day)
        r2_score_array.append(r2)

score_dict = {'distance': distance_array, 'day': date_array, 'r2': r2_score_array, "state": "GA"}
with open('/Users/zongrunli/Desktop/SEEmission/Visualization/Figure data/GA_relaxation.pkl', 'wb') as handle:
    pickle.dump(score_dict, handle, protocol=pickle.HIGHEST_PROTOCOL)


