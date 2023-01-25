from LandTypeHelper import max_counts
from LandTypeHelper import counts
import pandas as pd
import numpy as np
from datetime import datetime
import rasterio
import pyproj
from shapely.geometry import Point
from rasterstats import zonal_stats
import math


def seperate_ag_fires(filename):
    # nlcd .img data
    nlcd_files = {
        2013: "/Volumes/ZONGRUN_BACKUP_2/NLCD/nlcd_2013_land_cover_l48_20210604/nlcd_2013_land_cover_l48_20210604.img",
        2016: "/Volumes/ZONGRUN_BACKUP_2/NLCD/nlcd_2016_land_cover_l48_20210604/nlcd_2016_land_cover_l48_20210604.img",
        2019: "/Volumes/ZONGRUN_BACKUP_2/NLCD/nlcd_2019_land_cover_l48_20210604/nlcd_2019_land_cover_l48_20210604.img"}
    year_range = {2013: [2013, 2016],
                  2016: [2016, 2019],
                  2019: [2019, 2022]}

    dateparse = lambda x: datetime.strptime(x, '%Y-%m-%d')
    # read finn
    finn_df = pd.read_csv(filename, parse_dates=['DAY'], date_parser=dateparse)
    finn_id = finn_df["FIREID"].to_numpy()
    finn_lat = finn_df['LATI'].to_numpy()
    finn_lon = finn_df['LONGI'].to_numpy()
    finn_time = finn_df['DAY'].to_numpy()
    burn_area = finn_df["AREA"].to_numpy()
    nlcd_attr_res = np.zeros(finn_lat.shape)

    for year in nlcd_files.keys():
        nlcd_file = nlcd_files[year]
        with rasterio.open(nlcd_file) as r:
            ll_to_xy = pyproj.transformer.Transformer.from_crs('epsg:4326', r.crs)
            lower_time = datetime(year_range[year][0], 1, 1)
            upper_time = datetime(year_range[year][1], 1, 1)
            for i in range(0, len(finn_lat)):
                if (pd.Timestamp(finn_time[i]) >= lower_time) and (pd.Timestamp(finn_time[i]) < upper_time):
                    finn_y, finn_x = ll_to_xy.transform(finn_lat[i], finn_lon[i])
                    buffer_point_ctr = Point((finn_y, finn_x))
                    # change the buffer size based on burned area
                    # convert acres to m2
                    this_burn_area = burn_area[i] * 4046.8564224
                    # calculate the buffer size
                    buffer_length = math.sqrt(this_burn_area) / 2
                    if buffer_length <= 15:
                        print("To small: " + finn_id[i] + ", set the buffer length as 15m")
                        buffer_length = 15
                    buffer_grid = buffer_point_ctr.buffer(buffer_length, cap_style=3)
                    # print(this_burn_area)
                    # print(buffer_grid.area)
                    stats = zonal_stats(buffer_grid, nlcd_file,
                                        add_stats={'counts': counts})
                    main_type = max_counts(stats[0]["counts"])
                    nlcd_attr_res[i] = main_type

    finn_df['land_cover'] = nlcd_attr_res

    # NLCD
    legend = np.array([0, 11, 12, 21, 22, 23, 24, 31, 41, 42, 43, 51, 52, 71, 72, 73, 74, 81, 82, 90, 95])
    leg_str = np.array(
        ['No Data', 'Open Water', 'Perennial Ice/Snow', 'Developed, Open Space', 'Developed, Low Intensity',
         'Developed, Medium Intensity', 'Developed High Intensity', 'Barren Land (Rock/Sand/Clay)',
         'Deciduous Forest', 'Evergreen Forest', 'Mixed Forest', 'Dwarf Scrub', 'Shrub/Scrub',
         'Grassland/Herbaceous', 'Sedge/Herbaceous', 'Lichens', 'Moss', 'Pasture/Hay', 'Cultivated Crops',
         'Woody Wetlands', 'Emergent Herbaceous Wetlands'])
    # NLCD map
    nlcd_map = {}
    for i in range(0, len(leg_str)):
        nlcd_map[leg_str[i]] = legend[i]

    invalid_type = ["Open Water", "Perennial Ice/Snow", "Barren Land (Rock/Sand/Clay)"]
    agricultural_type = ["Cultivated Crops"]

    invalid_type_num = []
    agricultural_type_num = nlcd_map[agricultural_type[0]]
    for type_tmp in invalid_type:
        invalid_type_num.append(nlcd_map[type_tmp])

    agri_index = []
    invalid_index = []
    valid_index = []
    for index, row in finn_df.iterrows():
        land_cover = row["land_cover"]
        if land_cover == agricultural_type_num:
            agri_index.append(index)
        elif land_cover in invalid_type_num:
            invalid_index.append(index)
        else:
            valid_index.append(index)
    agri_df = finn_df.iloc[agri_index]
    invalid_df = finn_df.iloc[invalid_index]
    valid_df = finn_df.iloc[valid_index]

    agri_df = agri_df.reset_index(drop=True)
    invalid_df = invalid_df.reset_index(drop=True)
    valid_df = valid_df.reset_index(drop=True)

    return agri_df, invalid_df, valid_df