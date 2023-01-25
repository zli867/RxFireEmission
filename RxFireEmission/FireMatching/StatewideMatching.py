import numpy as np
from MatchingHelper import calculateDailyBurnedArea, commonData
from datetime import datetime
import statsmodels.api as sm
from sklearn.linear_model import LinearRegression


state_name = ["FL", "SC", "GA"]
permit_files = ["/Volumes/SERDP Modeling/RxEmissionData/permits/FL_2013_2021_permits_rx.csv",
                "/Volumes/SERDP Modeling/RxEmissionData/permits/Cleaned_SC_2013_2021_permits_rx.csv",
                "/Volumes/SERDP Modeling/RxEmissionData/permits/GA_2015_2020_permits_rx.csv"]
finn_files = ["/Volumes/SERDP Modeling/RxEmissionData/FINN/Rx/FL_Combined_MODIS_VIIRS_rx.csv",
           "/Volumes/SERDP Modeling/RxEmissionData/FINN/Rx/SC_Combined_MODIS_VIIRS_rx.csv",
           "/Volumes/SERDP Modeling/RxEmissionData/FINN/Rx/GA_Combined_MODIS_VIIRS_rx.csv"]

# state wide matching
# linear regression with intercept
for i in range(0, 3):
    if state_name[i] == "GA":
        start_time = datetime(2015, 1, 1)
    else:
        start_time = datetime(2013, 1, 1)
    end_time = datetime(2020, 12, 31)
    permit_time, permit_daily_area, finn_time, finn_daily_area = calculateDailyBurnedArea(finn_files[i], permit_files[i], start_time, end_time)
    common_time, finn_common, permit_common = commonData(permit_time, permit_daily_area, finn_time, finn_daily_area)
    # density plot
    x = finn_common
    y = permit_common
    x = x.reshape(-1, 1)
    X_ = sm.add_constant(x)
    model = sm.OLS(y, X_)
    results = model.fit()
    # Confident intervals
    cf = results.conf_int(alpha=0.05, cols=None)
    reg = LinearRegression(fit_intercept=True).fit(x, y)
    rsquare = reg.score(x, y)
    print("Current State is: " + state_name[i])
    print("R2 is: " + str(np.round(rsquare, 2)))