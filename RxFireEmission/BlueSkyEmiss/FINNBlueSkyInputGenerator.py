import BlueSkyHelper
import pandas as pd
from datetime import datetime
import json
import os
import numpy as np


finn_filename = "/home/zli867/FINNEmission/Data/FINN/SE_Combined_MODIS_VIIRS_rx.csv"
bluesky_input_dir = "/home/zli867/FINNEmissionFEPS/Data/bsp_input/"
bluesky_output_dir = "/home/zli867/FINNEmissionFEPS/Data/bsp_output/"
met_dir = "/home/zli867/NAM_12km/"
work_dir = "/home/zli867/FINNEmissionFEPS/Data/work_dir/"
config_file = "/home/zli867/FINNEmissionFEPS/Data/bsp_config/finn_config.json"

select_species = ["CO", "SO2", "NH3", "NOx", "PM10", "PM2.5", "VOC"]

dateparse = lambda x: datetime.strptime(x, '%Y-%m-%d')
finn_df = pd.read_csv(finn_filename, parse_dates=['DAY'], date_parser=dateparse)
# Run bluesky for each date
date_list = list(set(finn_df["DAY"]))
date_list.sort()
date_list = np.array(date_list)

# TODO: Revise start time and end time
start_time = datetime(2016, 7, 1)
end_time = datetime(2016, 12, 31)
date_list = date_list[(date_list >= start_time) & (date_list <= end_time)]

for select_date in date_list:
    fires = []
    select_finn = finn_df[finn_df["DAY"] == select_date]
    select_finn = select_finn.reset_index(drop=True)
    for index, row in select_finn.iterrows():
        fire_id = row["FIREID"]
        state = fire_id[0: 2]
        area = row["AREA"]
        day = row["DAY"]
        lat = row["LATI"]
        lon = row["LONGI"]
        fire = BlueSkyHelper.generateFirePlumerise(fire_id, lat, lon, day, area, state)
        fires.append(fire)
    # met data
    met_data = BlueSkyHelper.generateMetInfo(met_dir + str(select_date.year) + "/", select_date)
    result = {"fires": fires, "met": met_data}
    json_obj = json.dumps(result, indent=4)

    # Generate BlueSKY input
    input_filename = bluesky_input_dir + "SE" + select_date.strftime("%Y_%m_%d") + ".json"
    with open(input_filename, 'w') as fout:
        print(json_obj, file=fout)

    # for 13_08_17 and 15_11_29, we use WRF output, time_step = 1
    if select_date == datetime(2013, 8, 17) or select_date == datetime(2015, 11, 29):
        time_step = 1
    else:
        time_step = 3

    # Run BlueSKY
    work_dir_name = work_dir + "SE" + select_date.strftime("%Y_%m_%d")
    output_filename = bluesky_output_dir + "SE" + select_date.strftime("%Y_%m_%d") + "_out.json"
    print("Input file: " + input_filename)
    # TODO: Check the command
    command = "bsp -i " + input_filename + " -c " + config_file + " -o " + output_filename + " -C localmet.working_dir=" + work_dir_name + \
              " -C localmet.time_step=" + str(time_step) + \
              " localmet ecoregion fuelbeds fuelmoisture consumption emissions timeprofile plumerise"
    os.system(command)