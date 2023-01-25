import pandas as pd
from datetime import datetime
from util.GridBurnedAreaHelper import GridMatching
from util.GridBurnedAreaHelper import CMAQProj
from util.GridBurnedAreaHelper import CMAQGrid
import numpy as np
import pickle

fl_rec = "/Users/zongrunli/Desktop/SEEmission/Data/Permits/Agricultural/GA_2015_2020_permits_agr.csv"
dateparse = lambda x: datetime.strptime(x, '%Y-%m-%d')
rec_df = pd.read_csv(fl_rec, parse_dates=['Time'], date_parser=dateparse)

# Hyper-parameters
area_lower_bound = 0

# Apply filter
rec_df = rec_df[rec_df["Burned_Area"] >= area_lower_bound]

# Reset the index
rec_df = rec_df.reset_index(drop=True)

rec_date = rec_df["Time"]
rec_lat = rec_df["Lat"]
rec_lon = rec_df["Lon"]
rec_x = np.array([])
rec_y = np.array([])

# Generate Coordinate
mcip_gridcro2d = "/Users/zongrunli/Desktop/SEEmission/Data/CMAQ/GRIDCRO2D_0402_0407_4.nc"
cmaq_proj = CMAQProj(mcip_gridcro2d)
for i in range(0, len(rec_lon)):
    x_rec_tmp, y_rec_tmp = cmaq_proj(rec_lon[i], rec_lat[i])
    rec_x = np.append(rec_x, x_rec_tmp)
    rec_y = np.append(rec_y, y_rec_tmp)
rec_df['X'] = rec_x
rec_df['Y'] = rec_y

grid_x_ctr, grid_y_ctr = CMAQGrid(-75, -90, 35, 22, mcip_gridcro2d)
rec_date_set = set(rec_date)

m, p = grid_x_ctr.shape
grid_burn_area = np.zeros((len(rec_date_set), m, p))

# Grid Permits data
idx = 0
time_array = []
for select_date in rec_date_set:
    rec_select_idx = (rec_date == select_date)
    # select data
    rec_select = rec_df[rec_select_idx]
    # Selected Lat and Lon
    rec_x_select = rec_select['X'].to_numpy().reshape((-1, 1))
    rec_y_select = rec_select['Y'].to_numpy().reshape((-1, 1))
    rec_area_select = rec_select["Burned_Area"].to_numpy().reshape((-1, 1))
    rec_coord = np.hstack((rec_x_select, rec_y_select))
    grid_burn_area_tmp = GridMatching(rec_coord, rec_area_select, grid_x_ctr, grid_y_ctr)
    grid_burn_area[idx, :, :] = grid_burn_area_tmp
    time_array.append(select_date)
    idx = idx + 1

res = {}
res['Time'] = time_array
res['Burned_Area'] = grid_burn_area
res['X'] = grid_x_ctr
res['Y'] = grid_y_ctr
# Store data to pickle
with open('/Users/zongrunli/Desktop/SEEmission/Data/Grided Burned Area/Final Data/permit_ga_nlcd_agr.pickle', 'wb') as handle:
    pickle.dump(res, handle, protocol=pickle.HIGHEST_PROTOCOL)

