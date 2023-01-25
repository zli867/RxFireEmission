import pickle
import numpy as np
from util.GridBurnedAreaHelper import sampling
from util.GridBurnedAreaHelper import fastsampling
import statsmodels.api as sm
from sklearn.linear_model import LinearRegression

# You should generate the grid based burned area firstly and then execute this script
finn_files = ["/Users/zongrunli/Desktop/SEEmission/Data/Grided Burned Area/Final Data/finn_fl_nlcd.pickle",
              "/Users/zongrunli/Desktop/SEEmission/Data/Grided Burned Area/Final Data/finn_ga_nlcd.pickle",
              "/Users/zongrunli/Desktop/SEEmission/Data/Grided Burned Area/Final Data/finn_sc_nlcd.pickle"]
permit_files = ["/Users/zongrunli/Desktop/SEEmission/Data/Grided Burned Area/Final Data/permit_fl_nlcd.pickle",
                "/Users/zongrunli/Desktop/SEEmission/Data/Grided Burned Area/Final Data/Private/permit_ga_nlcd_private.pickle",
                "/Users/zongrunli/Desktop/SEEmission/Data/Grided Burned Area/Final Data/permit_sc_nlcd.pickle"]

finn = []
permit = []
for finn_file in finn_files:
    with open(finn_file, 'rb') as fp:
        finn_tmp = pickle.load(fp)
        finn.append(finn_tmp)
for permit_file in permit_files:
    with open(permit_file, 'rb') as fp:
        permit_tmp = pickle.load(fp)
        permit.append(permit_tmp)


# Combine all permits and FINN
def combineRecords(records_df_list):
    time = []
    for i in range(0, len(records_df_list)):
        time.extend(records_df_list[i]["Time"])
    _, m, n = records_df_list[0]["Burned_Area"].shape
    time = list(set(time))
    time.sort()
    burn_area = np.zeros((len(time), m, n))
    for i in range(0, len(time)):
        cur_time = time[i]
        for record_df in records_df_list:
            if cur_time in record_df["Time"]:
                idx = record_df["Time"].index(cur_time)
                burn_area[i, :, :] += record_df["Burned_Area"][idx, :, :]
            else:
                continue
    res = {}
    res["Time"] = time
    res["Burned_Area"] = burn_area
    res["X"] = records_df_list[0]["X"]
    res["Y"] = records_df_list[0]["Y"]
    return res


finn = combineRecords(finn)
permit = combineRecords(permit)

finn_time = finn['Time']
permit_time = permit['Time']
finn_area = finn['Burned_Area']
permit_area = permit['Burned_Area']
sample = True
fast = True
if sample:
    if fast:
        finn_area = fastsampling(finn_area)
        permit_area = fastsampling(permit_area)
    else:
        finn_area = sampling(finn_area)
        permit_area = sampling(permit_area)

grid_data = {
    "X": finn["X"],
    "Y": finn["Y"],
    "finn_time": finn['Time'],
    "permit_time": permit["Time"],
    # sampled area
    "finn_area": finn_area,
    "permit_area": permit_area
}
# save data if you want
with open('/Users/zongrunli/Desktop/SEEmission/Visualization/Figure data/grid_based_agr_data.pkl', 'wb') as handle:
    pickle.dump(grid_data, handle, protocol=pickle.HIGHEST_PROTOCOL)

# scaling factor
_, m, p = permit_area.shape
common_time = list(set(finn_time).intersection(set(permit_time)))
finn_area_common = np.array([])
permit_area_common = np.array([])
for i in range(0, len(common_time)):
    finn_idx = finn_time.index(common_time[i])
    permit_idx = permit_time.index(common_time[i])
    finn_area_tmp = finn['Burned_Area'][finn_idx, :, :]
    permit_area_tmp = permit['Burned_Area'][permit_idx, :, :]
    finn_area_tmp_flat = np.reshape(finn_area_tmp, (m*p, 1))
    permit_area_tmp_flat = np.reshape(permit_area_tmp, (m*p, 1))
    finn_sampled_flat = np.reshape(finn_area[finn_idx, :, :], (m*p, 1))
    permit_sampled_flat = np.reshape(permit_area[permit_idx, :, :], (m*p, 1))
    common_idx = (finn_area_tmp_flat > 0) & (permit_area_tmp_flat > 0)
    select_finn_area = finn_sampled_flat[common_idx]
    select_permit_area = permit_sampled_flat[common_idx]
    finn_area_common = np.append(finn_area_common, select_finn_area)
    permit_area_common = np.append(permit_area_common, select_permit_area)

# Statistical Evaluation
# x = finn_area_common.reshape(-1, 1), y = permit_area_common
finn_area_common = finn_area_common.reshape(-1, 1)
model = sm.OLS(permit_area_common, finn_area_common)
results = model.fit()
# Confident intervals
cf = results.conf_int(alpha=0.05, cols=None)
reg = LinearRegression(fit_intercept=False).fit(finn_area_common, permit_area_common)
rsquare = reg.score(finn_area_common, permit_area_common)
performance = 'y={:.2f}x \n slope: [{:.2f}, {:.2f}] \n $R^2$ = {:.2f}'.format(results.params[0], cf[0, 0], cf[0, 1], rsquare)
print(performance)

