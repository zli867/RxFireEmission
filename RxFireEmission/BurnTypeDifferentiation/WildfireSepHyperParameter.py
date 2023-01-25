import pandas as pd
import numpy as np
from datetime import datetime
from WildfireSeperation import seperate_wildfires


dateparse = lambda x: datetime.strptime(x, '%Y-%m-%d')
finn_file_name = "/Users/zongrunli/Desktop/SEEmission/Data/Wildfires/SE_Combined_MODIS_VIIRS_rx_wf.csv"
spatial_array = []
temporal_array = []
wildfire_num_array = []

for spatial_threshold in range(400, 1400, 200):
    for temporal_threshold in range(0, 1400, 200):
        # Read finn data
        finn_df = pd.read_csv(finn_file_name, parse_dates=['DAY'], date_parser=dateparse)

        res = seperate_wildfires(finn_df, spatial_threshold, temporal_threshold)
        finn_wf = res.copy()
        wildfire_num = len(np.unique(finn_wf["cluster_id"]))

        print("Wildfire nums from FINN: " + str(wildfire_num))
        spatial_array.append(spatial_threshold)
        temporal_array.append(temporal_threshold)
        wildfire_num_array.append(wildfire_num)

res_dict = {"spatial": spatial_array, "temporal": temporal_array, "wildfire_num": wildfire_num_array}
res_df = pd.DataFrame.from_dict(res_dict)
res_df.to_csv("Sensitivity_Wildfire_elbow.csv", index=False)