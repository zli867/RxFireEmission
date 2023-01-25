import numpy as np
from util.CompareHelper import pairwise_dist
from util.CompareHelper import sumByFireID
import pandas as pd
from datetime import datetime
from datetime import timedelta
from util.CompareHelper import removeDuplicateRecord
import pyproj
import matplotlib.pyplot as plt
from sklearn.linear_model import LinearRegression
from util.CompareHelper import penalty_score
from util.CompareHelper import pairwise_burn_diff


def distanceMapping(finn_df, rec_df):
    """
    Step 1: Mapping method: for each day, for each record, find the nearest FINN data, return <record_id, finn_id>
    Step 2: Mapping method: for each day, for each FINN, find the nearest record data, return <record_id, finn_id>
    Step 3: Choose the pairs which exists both in step 1 and step 2
    :param finn_df: DataFrame of FINN data
    :param rec_df: DataFrame of permits data
    :return: (record_id, finn_id)
    """
    # Date
    rec_date = rec_df['Time']
    finn_date = finn_df['DAY']
    # Coord
    sat_lat = finn_df["LATI"]
    sat_lon = finn_df["LONGI"]
    rec_lat = rec_df["Lat"]
    rec_lon = rec_df["Lon"]
    # X and Y
    sat_x = np.array([])
    sat_y = np.array([])
    rec_x = np.array([])
    rec_y = np.array([])

    # Convert lat, lon to x, y and calculate distance
    p = pyproj.Proj("+proj=utm +zone=16N, +north +ellps=WGS84 +datum=WGS84 +units=m +no_defs")
    for i in range(0, len(sat_lon)):
        x_sat_tmp, y_sat_tmp = p(sat_lon[i], sat_lat[i], inverse=False)
        sat_x = np.append(sat_x, x_sat_tmp)
        sat_y = np.append(sat_y, y_sat_tmp)

    for i in range(0, len(rec_lon)):
        x_rec_tmp, y_rec_tmp = p(rec_lon[i], rec_lat[i], inverse=False)
        rec_x = np.append(rec_x, x_rec_tmp)
        rec_y = np.append(rec_y, y_rec_tmp)

    finn_df['X'] = sat_x
    finn_df['Y'] = sat_y
    rec_df['X'] = rec_x
    rec_df['Y'] = rec_y
    df_res_stp_1 = pd.DataFrame(columns=('FIREID', 'Id', 'Dist'))
    # Step 1:
    finn_id_res = []
    record_id_res = []
    dist_res = []
    rec_date_set = set(rec_date)
    for select_date in rec_date_set:
        finn_select_idx = (finn_date == select_date)
        rec_select_idx = (rec_date == select_date)
        # select data
        finn_select = finn_df[finn_select_idx]
        rec_select = rec_df[rec_select_idx]
        # Selected Lat and Lon
        finn_x_select = finn_select['X']
        rec_x_select = rec_select['X']
        finn_y_select = finn_select['Y']
        rec_y_select = rec_select['Y']
        # Skip the date which do not have satellite or record
        if len(finn_x_select) == 0 or len(rec_x_select) == 0:
            continue
        else:
            finn_coord = np.vstack((finn_x_select, finn_y_select)).T
            rec_coord = np.vstack((rec_x_select, rec_y_select)).T
            dist = pairwise_dist(rec_coord, finn_coord)
            min_dist_select = np.min(dist, axis=1)
            min_dist_idx = np.argmin(dist, axis=1)
            id_finn = finn_select['FIREID'].to_numpy()[min_dist_idx]
            id_record = rec_select["Id"]
            finn_id_res.extend(id_finn)
            record_id_res.extend(id_record)
            dist_res.extend(min_dist_select)
    df_res_stp_1["FIREID"] = finn_id_res
    df_res_stp_1["Id"] = record_id_res
    df_res_stp_1["Dist"] = dist_res

    # Step 2:
    df_res_stp_2 = pd.DataFrame(columns=('FIREID', 'Id', 'Dist'))
    finn_id_res = []
    record_id_res = []
    dist_res = []
    sat_date_set = set(finn_date)
    for select_date in sat_date_set:
        finn_select_idx = (finn_date == select_date)
        rec_select_idx = (rec_date == select_date)
        # select data
        finn_select = finn_df[finn_select_idx]
        rec_select = rec_df[rec_select_idx]
        # Selected Lat and Lon
        finn_x_select = finn_select['X']
        rec_x_select = rec_select['X']
        finn_y_select = finn_select['Y']
        rec_y_select = rec_select['Y']
        # Skip the date which do not have satellite or record
        if len(finn_x_select) == 0 or len(rec_x_select) == 0:
            continue
        else:
            finn_coord = np.vstack((finn_x_select, finn_y_select)).T
            rec_coord = np.vstack((rec_x_select, rec_y_select)).T
            dist = pairwise_dist(finn_coord, rec_coord)
            min_dist_select = np.min(dist, axis=1)
            min_dist_idx = np.argmin(dist, axis=1)
            id_finn = finn_select['FIREID']
            id_record = rec_select["Id"].to_numpy()[min_dist_idx]
            finn_id_res.extend(id_finn)
            record_id_res.extend(id_record)
            dist_res.extend(min_dist_select)

    df_res_stp_2["FIREID"] = finn_id_res
    df_res_stp_2["Id"] = record_id_res
    df_res_stp_2["Dist"] = dist_res

    # Step 3
    res_df = pd.merge(df_res_stp_1[["FIREID", "Id"]], df_res_stp_2, how="inner", on=["FIREID", "Id"])
    # res and finn
    res_df = pd.merge(res_df, finn_df, how="inner", on=["FIREID"])
    # res and record
    res_df = pd.merge(res_df, rec_df, how="inner", on=["Id"])
    return res_df
    # res_df.to_csv("Test_333.csv", index=False)


def penaltyMapping(finn_df, rec_df):
    """

    :param finn_df:
    :param rec_df:
    :return:
    """
    # Date
    rec_date = rec_df['Time']
    finn_date = finn_df['DAY']
    # Coord
    sat_lat = finn_df["LATI"]
    sat_lon = finn_df["LONGI"]
    rec_lat = rec_df["Lat"]
    rec_lon = rec_df["Lon"]
    # X and Y
    sat_x = np.array([])
    sat_y = np.array([])
    rec_x = np.array([])
    rec_y = np.array([])

    # Convert lat, lon to x, y and calculate distance
    p = pyproj.Proj("+proj=utm +zone=16N, +north +ellps=WGS84 +datum=WGS84 +units=m +no_defs")
    for i in range(0, len(sat_lon)):
        x_sat_tmp, y_sat_tmp = p(sat_lon[i], sat_lat[i], inverse=False)
        sat_x = np.append(sat_x, x_sat_tmp)
        sat_y = np.append(sat_y, y_sat_tmp)

    for i in range(0, len(rec_lon)):
        x_rec_tmp, y_rec_tmp = p(rec_lon[i], rec_lat[i], inverse=False)
        rec_x = np.append(rec_x, x_rec_tmp)
        rec_y = np.append(rec_y, y_rec_tmp)

    finn_df['X'] = sat_x
    finn_df['Y'] = sat_y
    rec_df['X'] = rec_x
    rec_df['Y'] = rec_y
    df_res_stp_1 = pd.DataFrame(columns=('FIREID', 'Id', 'Dist'))
    # Step 1:
    finn_id_res = []
    record_id_res = []
    dist_res = []
    rec_date_set = set(rec_date)
    for select_date in rec_date_set:
        finn_select_idx = (finn_date == select_date)
        rec_select_idx = (rec_date == select_date)
        # select data
        finn_select = finn_df[finn_select_idx]
        rec_select = rec_df[rec_select_idx]
        # Selected Lat and Lon
        finn_x_select = finn_select['X']
        rec_x_select = rec_select['X']
        finn_y_select = finn_select['Y']
        rec_y_select = rec_select['Y']
        rec_area_select = rec_select["Burned_Area"]
        finn_area_select = finn_select["AREA"]
        # Skip the date which do not have satellite or record
        if len(finn_x_select) == 0 or len(rec_x_select) == 0:
            continue
        else:
            finn_coord = np.vstack((finn_x_select, finn_y_select, finn_area_select)).T
            rec_coord = np.vstack((rec_x_select, rec_y_select, rec_area_select)).T
            dist = penalty_score(rec_coord, finn_coord)
            min_dist_select = np.min(dist, axis=1)
            min_dist_idx = np.argmin(dist, axis=1)
            id_finn = finn_select['FIREID'].to_numpy()[min_dist_idx]
            id_record = rec_select["Id"]
            finn_id_res.extend(id_finn)
            record_id_res.extend(id_record)
            dist_res.extend(min_dist_select)
    df_res_stp_1["FIREID"] = finn_id_res
    df_res_stp_1["Id"] = record_id_res
    df_res_stp_1["Dist"] = dist_res

    # Step 2:
    df_res_stp_2 = pd.DataFrame(columns=('FIREID', 'Id', 'Dist'))
    finn_id_res = []
    record_id_res = []
    dist_res = []
    sat_date_set = set(finn_date)
    for select_date in sat_date_set:
        finn_select_idx = (finn_date == select_date)
        rec_select_idx = (rec_date == select_date)
        # select data
        finn_select = finn_df[finn_select_idx]
        rec_select = rec_df[rec_select_idx]
        # Selected Lat and Lon
        finn_x_select = finn_select['X']
        rec_x_select = rec_select['X']
        finn_y_select = finn_select['Y']
        rec_y_select = rec_select['Y']
        rec_area_select = rec_select["Burned_Area"]
        finn_area_select = finn_select["AREA"]
        # Skip the date which do not have satellite or record
        if len(finn_x_select) == 0 or len(rec_x_select) == 0:
            continue
        else:
            finn_coord = np.vstack((finn_x_select, finn_y_select, finn_area_select)).T
            rec_coord = np.vstack((rec_x_select, rec_y_select, rec_area_select)).T
            dist = penalty_score(finn_coord, rec_coord)
            min_dist_select = np.min(dist, axis=1)
            min_dist_idx = np.argmin(dist, axis=1)
            id_finn = finn_select['FIREID']
            id_record = rec_select["Id"].to_numpy()[min_dist_idx]
            finn_id_res.extend(id_finn)
            record_id_res.extend(id_record)
            dist_res.extend(min_dist_select)

    df_res_stp_2["FIREID"] = finn_id_res
    df_res_stp_2["Id"] = record_id_res
    df_res_stp_2["Dist"] = dist_res

    # Step 3
    res_df = pd.merge(df_res_stp_1[["FIREID", "Id"]], df_res_stp_2, how="inner", on=["FIREID", "Id"])
    # res and finn
    res_df = pd.merge(res_df, finn_df, how="inner", on=["FIREID"])
    # res and record
    res_df = pd.merge(res_df, rec_df, how="inner", on=["Id"])
    res_df["Dist"] = np.sqrt((res_df["X_x"] - res_df["X_y"])**2 + (res_df["Y_x"] - res_df["Y_y"])**2)
    res_df.to_csv("Test_penalty.csv", index=False)


def relaxationDate(finn_df, rec_df, threshold):
    """
    Step 1:
    For each day i, extract all records and satellite data in <i - threshold, i + threshold> period.
    For each record, find the nearest satellite data in this pool. Return <Record id, FINN id>

    Step 2:
    For each day i, extract all records and satellite data in <i - threshold, i + threshold> period.
    For each satellite, find the nearest record data in this pool. Return <Record id, FINN id>

    Step 3:
    Choose the pairs which exists both in step 1 and step 2

    :param finn_df:
    :param rec_df:
    :param threshold:
    :return:
    """
    pass


def relaxationDist(finn_df, rec_df, threshold):
    """
    Step 1:
    For each day i, for each record, find all satellite data has a distance with the record
    closer than threshold. Match the record and selected satellite which has smallest difference
    in burned area. Return <Record id, FINN id>

    Step 2:
    For each day i, for each satellite, find all record data has a distance with the satellite
    closer than threshold. Match the record and selected satellite which has smallest difference
    in burned area. Return <Record id, FINN id>

    Step 3:
    Choose the pairs which exists both in step 1 and step 2

    :param finn_df: DataFrame of FINN data
    :param rec_df: DataFrame of permits data
    :param threshold: relaxation distance threshold (unit: m)
    :return: (record_id, finn_id)
    """
    # Date
    rec_date = rec_df['Time']
    finn_date = finn_df['DAY']
    # Coord
    sat_lat = finn_df["LATI"]
    sat_lon = finn_df["LONGI"]
    rec_lat = rec_df["Lat"]
    rec_lon = rec_df["Lon"]
    # X and Y
    sat_x = np.array([])
    sat_y = np.array([])
    rec_x = np.array([])
    rec_y = np.array([])

    # Convert lat, lon to x, y and calculate distance
    p = pyproj.Proj("+proj=utm +zone=16N, +north +ellps=WGS84 +datum=WGS84 +units=m +no_defs")
    for i in range(0, len(sat_lon)):
        x_sat_tmp, y_sat_tmp = p(sat_lon[i], sat_lat[i], inverse=False)
        sat_x = np.append(sat_x, x_sat_tmp)
        sat_y = np.append(sat_y, y_sat_tmp)

    for i in range(0, len(rec_lon)):
        x_rec_tmp, y_rec_tmp = p(rec_lon[i], rec_lat[i], inverse=False)
        rec_x = np.append(rec_x, x_rec_tmp)
        rec_y = np.append(rec_y, y_rec_tmp)

    finn_df['X'] = sat_x
    finn_df['Y'] = sat_y
    rec_df['X'] = rec_x
    rec_df['Y'] = rec_y
    df_res_stp_1 = pd.DataFrame(columns=('FIREID', 'Id'))

    # Step 1:
    finn_id_res = []
    record_id_res = []
    rec_date_set = set(rec_date)
    for select_date in rec_date_set:
        finn_select_idx = (finn_date == select_date)
        rec_select_idx = (rec_date == select_date)
        # select data
        finn_select = finn_df[finn_select_idx]
        rec_select = rec_df[rec_select_idx]
        # Selected Lat and Lon
        finn_x_select = finn_select['X'].to_numpy()
        rec_x_select = rec_select['X'].to_numpy()
        finn_y_select = finn_select['Y'].to_numpy()
        rec_y_select = rec_select['Y'].to_numpy()
        rec_area_select = rec_select["Burned_Area"].to_numpy()
        finn_area_select = finn_select["AREA"].to_numpy()
        id_finn = finn_select['FIREID'].to_numpy()
        id_record = rec_select["Id"].to_numpy()
        # Skip the date which do not have satellite or record
        if len(finn_x_select) == 0 or len(rec_x_select) == 0:
            continue
        else:
            finn_coord = np.vstack((finn_x_select, finn_y_select)).T
            rec_coord = np.vstack((rec_x_select, rec_y_select)).T
            dist = pairwise_dist(rec_coord, finn_coord)
            valid_address_msk = np.ones(dist.shape) * np.nan
            valid_address_msk[dist <= threshold] = 0
            burn_diff = pairwise_burn_diff(rec_area_select, finn_area_select)
            valid_burn_diff = burn_diff + valid_address_msk
            # Delete the record which does not have any finn candidates based on threshold
            invalid_rows_idx = np.isnan(valid_burn_diff).all(axis=1)
            valid_burn_diff = valid_burn_diff[~invalid_rows_idx]
            id_record = id_record[~invalid_rows_idx]
            if len(id_record) > 0:
                min_burn_idx = np.nanargmin(valid_burn_diff, axis=1)
                finn_id_res.extend(id_finn[min_burn_idx])
                record_id_res.extend(id_record)
    df_res_stp_1["FIREID"] = finn_id_res
    df_res_stp_1["Id"] = record_id_res

    # Step 2
    df_res_stp_2 = pd.DataFrame(columns=('FIREID', 'Id'))
    finn_id_res = []
    record_id_res = []
    sat_date_set = set(finn_date)
    for select_date in sat_date_set:
        finn_select_idx = (finn_date == select_date)
        rec_select_idx = (rec_date == select_date)
        # select data
        finn_select = finn_df[finn_select_idx]
        rec_select = rec_df[rec_select_idx]
        # Selected Lat and Lon
        finn_x_select = finn_select['X'].to_numpy()
        rec_x_select = rec_select['X'].to_numpy()
        finn_y_select = finn_select['Y'].to_numpy()
        rec_y_select = rec_select['Y'].to_numpy()
        rec_area_select = rec_select["Burned_Area"].to_numpy()
        finn_area_select = finn_select["AREA"].to_numpy()
        id_finn = finn_select['FIREID'].to_numpy()
        id_record = rec_select["Id"].to_numpy()
        # Skip the date which do not have satellite or record
        if len(finn_x_select) == 0 or len(rec_x_select) == 0:
            continue
        else:
            finn_coord = np.vstack((finn_x_select, finn_y_select)).T
            rec_coord = np.vstack((rec_x_select, rec_y_select)).T
            dist = pairwise_dist(finn_coord, rec_coord)
            valid_address_msk = np.ones(dist.shape) * np.nan
            valid_address_msk[dist <= threshold] = 0
            burn_diff = pairwise_burn_diff(finn_area_select, rec_area_select)
            valid_burn_diff = burn_diff + valid_address_msk
            # Delete the FINN which does not have any record candidates based on threshold
            invalid_rows_idx = np.isnan(valid_burn_diff).all(axis=1)
            valid_burn_diff = valid_burn_diff[~invalid_rows_idx]
            id_finn = id_finn[~invalid_rows_idx]
            if len(id_finn) > 0:
                min_burn_idx = np.nanargmin(valid_burn_diff, axis=1)
                finn_id_res.extend(id_finn)
                record_id_res.extend(id_record[min_burn_idx])

    df_res_stp_2["FIREID"] = finn_id_res
    df_res_stp_2["Id"] = record_id_res

    # Step 3
    res_df = pd.merge(df_res_stp_1[["FIREID", "Id"]], df_res_stp_2, how="inner", on=["FIREID", "Id"])
    # res and finn
    res_df = pd.merge(res_df, finn_df, how="inner", on=["FIREID"])
    # res and record
    res_df = pd.merge(res_df, rec_df, how="inner", on=["Id"])
    res_df['Dist'] = np.sqrt((res_df['X_x'] - res_df['X_y'])**2 + (res_df['Y_x'] - res_df['Y_y'])**2)
    res_df.to_csv("Test_dist_threshold.csv", index=False)


def relaxationDistDate(finn_df, rec_df, dist_threshold, day_threshold):
    """
    Step 1:
    For each day i, we select the record and finn btw day <i-day_threshold, i+day_threshold>.
    For each record, find all satellite data has a distance with the record
    closer than threshold. Match the record and selected satellite which has smallest difference
    in burned area. Return <Record id, FINN id>

    Step 2:
    For each day i, we select the record and finn btw day <i-day_threshold, i+day_threshold>.
    For each satellite, find all record data has a distance with the satellite
    closer than threshold. Match the record and selected satellite which has smallest difference
    in burned area. Return <Record id, FINN id>

    Step 3:
    Choose the pairs which exists both in step 1 and step 2

    :param finn_df: DataFrame of FINN data
    :param rec_df: DataFrame of permits data
    :param dist_threshold: relaxation distance threshold (unit: m)
    :param day_threshold: relaxation date threshold (unit: day)
    :return: (record_id, finn_id)
    """
    # Date
    rec_date = rec_df['Time']
    finn_date = finn_df['DAY']
    # Coord
    sat_lat = finn_df["LATI"]
    sat_lon = finn_df["LONGI"]
    rec_lat = rec_df["Lat"]
    rec_lon = rec_df["Lon"]
    # X and Y
    sat_x = np.array([])
    sat_y = np.array([])
    rec_x = np.array([])
    rec_y = np.array([])

    # Convert lat, lon to x, y and calculate distance
    p = pyproj.Proj("+proj=utm +zone=16N, +north +ellps=WGS84 +datum=WGS84 +units=m +no_defs")
    for i in range(0, len(sat_lon)):
        x_sat_tmp, y_sat_tmp = p(sat_lon[i], sat_lat[i], inverse=False)
        sat_x = np.append(sat_x, x_sat_tmp)
        sat_y = np.append(sat_y, y_sat_tmp)

    for i in range(0, len(rec_lon)):
        x_rec_tmp, y_rec_tmp = p(rec_lon[i], rec_lat[i], inverse=False)
        rec_x = np.append(rec_x, x_rec_tmp)
        rec_y = np.append(rec_y, y_rec_tmp)

    finn_df['X'] = sat_x
    finn_df['Y'] = sat_y
    rec_df['X'] = rec_x
    rec_df['Y'] = rec_y
    df_res_stp_1 = pd.DataFrame(columns=('FIREID', 'Id'))

    # Step 1:
    finn_id_res = []
    record_id_res = []
    rec_date_set = set(rec_date)
    for select_date in rec_date_set:
        lower_date = select_date - timedelta(days=day_threshold)
        upper_date = select_date + timedelta(days=day_threshold)
        finn_select_idx = (finn_date >= lower_date) & (finn_date <= upper_date)
        rec_select_idx = (rec_date >= lower_date) & (rec_date <= upper_date)
        # select data
        finn_select = finn_df[finn_select_idx]
        rec_select = rec_df[rec_select_idx]
        # Selected Lat and Lon
        finn_x_select = finn_select['X'].to_numpy()
        rec_x_select = rec_select['X'].to_numpy()
        finn_y_select = finn_select['Y'].to_numpy()
        rec_y_select = rec_select['Y'].to_numpy()
        rec_area_select = rec_select["Burned_Area"].to_numpy()
        finn_area_select = finn_select["AREA"].to_numpy()
        id_finn = finn_select['FIREID'].to_numpy()
        id_record = rec_select["Id"].to_numpy()
        # Skip the date which do not have satellite or record
        if len(finn_x_select) == 0 or len(rec_x_select) == 0:
            continue
        else:
            finn_coord = np.vstack((finn_x_select, finn_y_select)).T
            rec_coord = np.vstack((rec_x_select, rec_y_select)).T
            dist = pairwise_dist(rec_coord, finn_coord)
            valid_address_msk = np.ones(dist.shape) * np.nan
            valid_address_msk[dist <= dist_threshold] = 0
            burn_diff = pairwise_burn_diff(rec_area_select, finn_area_select)
            valid_burn_diff = burn_diff + valid_address_msk
            # Delete the record which does not have any finn candidates based on threshold
            invalid_rows_idx = np.isnan(valid_burn_diff).all(axis=1)
            valid_burn_diff = valid_burn_diff[~invalid_rows_idx]
            id_record = id_record[~invalid_rows_idx]
            if len(id_record) > 0:
                min_burn_idx = np.nanargmin(valid_burn_diff, axis=1)
                finn_id_res.extend(id_finn[min_burn_idx])
                record_id_res.extend(id_record)
    df_res_stp_1["FIREID"] = finn_id_res
    df_res_stp_1["Id"] = record_id_res

    # Step 2
    df_res_stp_2 = pd.DataFrame(columns=('FIREID', 'Id'))
    finn_id_res = []
    record_id_res = []
    sat_date_set = set(finn_date)
    for select_date in sat_date_set:
        lower_date = select_date - timedelta(days=day_threshold)
        upper_date = select_date + timedelta(days=day_threshold)
        finn_select_idx = (finn_date >= lower_date) & (finn_date <= upper_date)
        rec_select_idx = (rec_date >= lower_date) & (rec_date <= upper_date)
        # select data
        finn_select = finn_df[finn_select_idx]
        rec_select = rec_df[rec_select_idx]
        # Selected Lat and Lon
        finn_x_select = finn_select['X'].to_numpy()
        rec_x_select = rec_select['X'].to_numpy()
        finn_y_select = finn_select['Y'].to_numpy()
        rec_y_select = rec_select['Y'].to_numpy()
        rec_area_select = rec_select["Burned_Area"].to_numpy()
        finn_area_select = finn_select["AREA"].to_numpy()
        id_finn = finn_select['FIREID'].to_numpy()
        id_record = rec_select["Id"].to_numpy()
        # Skip the date which do not have satellite or record
        if len(finn_x_select) == 0 or len(rec_x_select) == 0:
            continue
        else:
            finn_coord = np.vstack((finn_x_select, finn_y_select)).T
            rec_coord = np.vstack((rec_x_select, rec_y_select)).T
            dist = pairwise_dist(finn_coord, rec_coord)
            valid_address_msk = np.ones(dist.shape) * np.nan
            valid_address_msk[dist <= dist_threshold] = 0
            burn_diff = pairwise_burn_diff(finn_area_select, rec_area_select)
            valid_burn_diff = burn_diff + valid_address_msk
            # Delete the FINN which does not have any record candidates based on threshold
            invalid_rows_idx = np.isnan(valid_burn_diff).all(axis=1)
            valid_burn_diff = valid_burn_diff[~invalid_rows_idx]
            id_finn = id_finn[~invalid_rows_idx]
            if len(id_finn) > 0:
                min_burn_idx = np.nanargmin(valid_burn_diff, axis=1)
                finn_id_res.extend(id_finn)
                record_id_res.extend(id_record[min_burn_idx])

    df_res_stp_2["FIREID"] = finn_id_res
    df_res_stp_2["Id"] = record_id_res

    # Step 3
    res_df = pd.merge(df_res_stp_1[["FIREID", "Id"]], df_res_stp_2, how="inner", on=["FIREID", "Id"])
    # Duplicate (this method could have!?)
    res_df = res_df.drop_duplicates(subset=['FIREID', 'Id'], keep='last')
    # res and finn
    res_df = pd.merge(res_df, finn_df, how="inner", on=["FIREID"])
    # res and record
    res_df = pd.merge(res_df, rec_df, how="inner", on=["Id"])
    res_df['Dist'] = np.sqrt((res_df['X_x'] - res_df['X_y'])**2 + (res_df['Y_x'] - res_df['Y_y'])**2)

    return res_df


def calculateDailyBurnedArea(finn_file, permit_file, start_time, end_time):
    dateparse = lambda x: datetime.strptime(x, '%Y-%m-%d')
    permits = pd.read_csv(permit_file, parse_dates=['Time'], date_parser=dateparse)
    finn = pd.read_csv(finn_file, parse_dates=['DAY'], date_parser=dateparse)
    # 2013 to 2020
    permits = permits[(permits['Time'] <= end_time) & (permits['Time'] >= start_time)]
    finn = finn[(finn["DAY"] <= end_time) & (finn["DAY"] >= start_time)]
    permit_daily_area = permits.groupby('Time').sum()['Burned_Area']
    permit_time = list(permit_daily_area.index)
    permit_daily_area = permit_daily_area.to_numpy()
    finn_daily_area = finn.groupby('DAY').sum()['AREA']
    finn_time = list(finn_daily_area.index)
    finn_daily_area = finn_daily_area.to_numpy()
    return permit_time, permit_daily_area, finn_time, finn_daily_area


def commonData(permit_time, permit_daily_area, finn_time, finn_daily_area):
    common_time = list(set(finn_time).intersection(set(permit_time)))
    finn_common = []
    permit_common = []
    for i in range(0, len(finn_time)):
        if finn_time[i] in common_time:
            finn_common.append(finn_daily_area[i])
    for i in range(0, len(permit_time)):
        if permit_time[i] in common_time:
            permit_common.append(permit_daily_area[i])
    finn_common = np.array(finn_common)
    permit_common = np.array(permit_common)
    return common_time, finn_common, permit_common