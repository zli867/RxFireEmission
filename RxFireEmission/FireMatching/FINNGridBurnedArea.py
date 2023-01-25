import pandas as pd
from datetime import datetime
from util.GridBurnedAreaHelper import GridMatching
from util.GridBurnedAreaHelper import CMAQProj
from util.GridBurnedAreaHelper import CMAQGrid
import numpy as np
import pickle

fl_finn = "/Users/zongrunli/Desktop/SEEmission/Data/FINN/MODIS VIIRS/FL_Combined_MODIS_VIIRS_agr.csv"
dateparse = lambda x: datetime.strptime(x, '%Y-%m-%d')
finn_df = pd.read_csv(fl_finn, parse_dates=['DAY'], date_parser=dateparse)

# Hyper-parameters
area_lower_bound = 0

# Apply filter
finn_df = finn_df[finn_df["AREA"] >= area_lower_bound]

# Reset the index
finn_df = finn_df.reset_index(drop=True)

finn_date = finn_df['DAY']
sat_lat = finn_df["LATI"]
sat_lon = finn_df["LONGI"]
sat_x = np.array([])
sat_y = np.array([])

# Generate Coordinate
mcip_gridcro2d = "/Users/zongrunli/Desktop/RxFireEmission/data/CMAQ_Grid/GRIDCRO2D_0402_0407_4.nc"
cmaq_proj = CMAQProj(mcip_gridcro2d)
for i in range(0, len(sat_lon)):
    x_sat_tmp, y_sat_tmp = cmaq_proj(sat_lon[i], sat_lat[i])
    sat_x = np.append(sat_x, x_sat_tmp)
    sat_y = np.append(sat_y, y_sat_tmp)
finn_df['X'] = sat_x
finn_df['Y'] = sat_y

grid_x_ctr, grid_y_ctr = CMAQGrid(-75, -90, 35, 22, mcip_gridcro2d)
finn_date_set = set(finn_date)

m, p = grid_x_ctr.shape
grid_burn_area = np.zeros((len(finn_date_set), m, p))
# Grid Permits data
idx = 0
time_array = []
for select_date in finn_date_set:
    finn_select_idx = (finn_date == select_date)
    # select data
    finn_select = finn_df[finn_select_idx]
    # Selected Lat and Lon
    finn_x_select = finn_select['X'].to_numpy().reshape((-1, 1))
    finn_y_select = finn_select['Y'].to_numpy().reshape((-1, 1))
    finn_area_select = finn_select["AREA"].to_numpy().reshape((-1, 1))
    finn_coord = np.hstack((finn_x_select, finn_y_select))
    grid_burn_area_tmp = GridMatching(finn_coord, finn_area_select, grid_x_ctr, grid_y_ctr)
    grid_burn_area[idx, :, :] = grid_burn_area_tmp
    time_array.append(select_date)
    idx = idx + 1

res = {}
res['Time'] = time_array
res['Burned_Area'] = grid_burn_area
res['X'] = grid_x_ctr
res['Y'] = grid_y_ctr
# Store data to pickle
with open('/Users/zongrunli/Desktop/SEEmission/Data/Grided Burned Area/Final Data/finn_fl_nlcd_agr.pickle', 'wb') as handle:
    pickle.dump(res, handle, protocol=pickle.HIGHEST_PROTOCOL)