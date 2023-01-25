import netCDF4 as nc
import pyproj
import numpy as np
import json
from datetime import datetime, timedelta
import matplotlib.pyplot as plt
from util import GeoHelper
from util.GridBurnedAreaHelper import CMAQProj
import pandas as pd
from util.GridBurnedAreaHelper import CMAQGrid


def tons_to_kg(emiss):
    return emiss * 1000


def tons_to_mole(emiss, molecule_weight):
    res = emiss * 1000 * 1000/molecule_weight
    return res


def datetime_range(start, end, delta):
    time_array = []
    current = start
    time_array.append(current)
    while current < end:
        current += delta
        time_array.append(current)
    return time_array


def CMAQGrid2D(mcip_gridcro2d):
    """

    :param mcip_gridcro2d: CMAQ MCIP grid cros 2D output
    :return: a dictionary: {"crs": projection,
                            "X_ctr": x_center_grid,
                            "Y_ctr": y_center_grid,
                            "X_bdry": [x_min, x_max],
                            "Y_bdry": [y_min, y_max]}
    """
    ds = nc.Dataset(mcip_gridcro2d)
    lat_1 = ds.getncattr('P_ALP')
    lat_2 = ds.getncattr('P_BET')
    lat_0 = ds.getncattr('YCENT')
    lon_0 = ds.getncattr('XCENT')
    crs = pyproj.Proj("+proj=lcc +a=6370000.0 +b=6370000.0 +lat_1=" + str(lat_1)
                      + " +lat_2=" + str(lat_2) + " +lat_0=" + str(lat_0) +
                      " +lon_0=" + str(lon_0))
    xcell = ds.getncattr('XCELL')
    ycell = ds.getncattr('YCELL')
    xorig = ds.getncattr('XORIG')
    yorig = ds.getncattr('YORIG')

    ncols = ds.getncattr('NCOLS')
    nrows = ds.getncattr('NROWS')

    #> for X, Y cell centers
    x_center_range = np.linspace(xorig+xcell/2, (xorig+xcell/2)+xcell*(ncols-1), ncols)
    y_center_range = np.linspace(yorig+ycell/2, (yorig+ycell/2)+ycell*(nrows-1), nrows)

    Xcenters, Ycenters = np.meshgrid(x_center_range, y_center_range)

    #> for X, Y cell boundaries (i.e., cell corners)
    x_bound_range = np.linspace(xorig, xorig+xcell*ncols, ncols+1)
    y_bound_range = np.linspace(yorig, yorig+ycell*nrows, nrows+1)

    Xbounds, Ybounds = np.meshgrid(x_bound_range, y_bound_range)

    x_max = np.max(Xbounds)
    x_min = np.min(Xbounds)
    y_max = np.max(Ybounds)
    y_min = np.min(Ybounds)

    res_dict = {"crs": crs, "X_ctr": Xcenters, "Y_ctr": Ycenters, "X_bdry": [x_min, x_max], "Y_bdry": [y_min, y_max]}
    return res_dict


def CMAQGrid3D(metcros3d):
    met_ds = nc.Dataset(metcros3d)
    cmaq_height = met_ds['ZF'][:]
    time_data = met_ds['TFLAG'][:]
    lat_1 = met_ds.getncattr('P_ALP')
    lat_2 = met_ds.getncattr('P_BET')
    lat_0 = met_ds.getncattr('YCENT')
    lon_0 = met_ds.getncattr('XCENT')
    crs = pyproj.Proj("+proj=lcc +a=6370000.0 +b=6370000.0 +lat_1=" + str(lat_1)
                      + " +lat_2=" + str(lat_2) + " +lat_0=" + str(lat_0) +
                      " +lon_0=" + str(lon_0))
    xcell = met_ds.getncattr('XCELL')
    ycell = met_ds.getncattr('YCELL')
    xorig = met_ds.getncattr('XORIG')
    yorig = met_ds.getncattr('YORIG')

    ncols = met_ds.getncattr('NCOLS')
    nrows = met_ds.getncattr('NROWS')

    #> for X, Y cell centers
    x_center_range = np.linspace(xorig+xcell/2, (xorig+xcell/2)+xcell*(ncols-1), ncols)
    y_center_range = np.linspace(yorig+ycell/2, (yorig+ycell/2)+ycell*(nrows-1), nrows)

    Xcenters, Ycenters = np.meshgrid(x_center_range, y_center_range)

    #> for X, Y cell boundaries (i.e., cell corners)
    x_bound_range = np.linspace(xorig, xorig+xcell*ncols, ncols+1)
    y_bound_range = np.linspace(yorig, yorig+ycell*nrows, nrows+1)

    Xbounds, Ybounds = np.meshgrid(x_bound_range, y_bound_range)

    x_max = np.max(Xbounds)
    x_min = np.min(Xbounds)
    y_max = np.max(Ybounds)
    y_min = np.min(Ybounds)

    cmaq_time_array = []
    for i in range(0, time_data.shape[0]):
        time_data_tmp = time_data[i, 0, :]
        time_str = str(time_data_tmp[0]) + str(time_data_tmp[1]).rjust(6, '0')
        parsed = datetime.strptime(time_str, '%Y%j%H%M%S')
        cmaq_time_array.append(parsed)

    res_dict = {"crs": crs, "X_ctr": Xcenters, "Y_ctr": Ycenters, "X_bdry": [x_min, x_max], "Y_bdry": [y_min, y_max],
                "height": cmaq_height, "time": cmaq_time_array}
    return res_dict


def hourlyFraction(timeprofile, utc_offset):
    """

    :param timeprofile: timeprofile form bsp_output, a dict
    :param utc_offset: utc_offset from bsp_output, a string
    :return: a dictionary: {"flaming": [hourly fraction], "smoldering": [hourly fraction], "residual": hourly fraction}
    """
    # convert utc_offset to time delta
    negative = False
    if utc_offset[0] == "-":
        delta = datetime.strptime(utc_offset[1:], "%H:%M") - datetime.strptime("00:00", "%H:%M")
        negative = True
    else:
        delta = datetime.strptime(utc_offset, "%H:%M") - datetime.strptime("00:00", "%H:%M")
    # generate hourly fraction
    flaming_hourly_frac = np.zeros(25)
    smoldering_hourly_frac = np.zeros(25)
    residual_hourly_farc = np.zeros(25)
    for key in timeprofile.keys():
        datetime_object = datetime.strptime(key, '%Y-%m-%dT%H:%M:%S')
        # local time to utc
        if negative:
            utc_date = datetime_object + delta
        else:
            utc_date = datetime_object - delta
        if utc_date.hour == 0 and utc_date.day != datetime_object.day:
            idx = 24
        else:
            idx = utc_date.hour
        flaming_hourly_frac[idx] = timeprofile[key]['flaming']
        smoldering_hourly_frac[idx] = timeprofile[key]['smoldering']
        residual_hourly_farc[idx] = timeprofile[key]['residual']
    return {"flaming_hourly_frac": flaming_hourly_frac,
            "smoldering_hourly_frac": smoldering_hourly_frac,
            "residual_hourly_farc": residual_hourly_farc}


def verticalHourlyFraction(timeprofile, plumerise, utc_offset, mcip_time, mcip_height):
    negative = False
    if utc_offset[0] == "-":
        delta = datetime.strptime(utc_offset[1:], "%H:%M") - datetime.strptime("00:00", "%H:%M")
        negative = True
    else:
        delta = datetime.strptime(utc_offset, "%H:%M") - datetime.strptime("00:00", "%H:%M")

    # temporal fraction * height fraction
    # generate hourly fraction
    lay = mcip_height.shape[1]
    flaming_frac = np.zeros((len(mcip_time), lay))
    smoldering_frac = np.zeros((len(mcip_time), lay))
    residual_farc = np.zeros((len(mcip_time), lay))
    for key in timeprofile.keys():
        datetime_object = datetime.strptime(key, '%Y-%m-%dT%H:%M:%S')
        # local time to utc
        if negative:
            utc_date = datetime_object + delta
        else:
            utc_date = datetime_object - delta
        time_idx = mcip_time.index(utc_date)
        # calculate vertical fraction
        fractions = np.zeros(lay)
        vertical_heights_bsp = plumerise[key]["heights"]
        max_plumerise = np.max(vertical_heights_bsp)
        min_plumerise = np.min(vertical_heights_bsp)
        mcip_height_tmp = mcip_height[time_idx, :]
        for i in range(0, len(mcip_height_tmp)):
            if i == 0:
                bottom = 0
                top = mcip_height_tmp[i]
            else:
                bottom = mcip_height_tmp[i - 1]
                top = mcip_height_tmp[i]
            if bottom >= min_plumerise and top <= max_plumerise:
                frac_tmp = (top - bottom) / (max_plumerise - min_plumerise)
            elif bottom <= min_plumerise <= top:
                if top <= max_plumerise:
                    frac_tmp = (top - min_plumerise) / (max_plumerise - min_plumerise)
                else:
                    frac_tmp = 1
            elif bottom <= max_plumerise <= top:
                frac_tmp = (max_plumerise - bottom) / (max_plumerise - min_plumerise)
            else:
                frac_tmp = 0
            fractions[i] = frac_tmp
        flaming_frac[time_idx, :] = timeprofile[key]['flaming'] * fractions
        smoldering_frac[time_idx, :] = timeprofile[key]['smoldering'] * fractions
        residual_farc[time_idx, :] = timeprofile[key]['residual'] * fractions
    return {"flaming_hourly_frac": flaming_frac,
            "smoldering_hourly_frac": smoldering_frac,
            "residual_hourly_farc": residual_farc}


def classifiedEmission(fuelbeds, select_species):
    """

    :param fuelbeds:
    :param select_species:
    :return:
    """
    # initialize flaming residual and smoldering emissions
    flaming = {}
    for select_specie in select_species:
        flaming[select_specie] = 0
    smoldering = {}
    for select_specie in select_species:
        smoldering[select_specie] = 0
    residual = {}
    for select_specie in select_species:
        residual[select_specie] = 0

    for fuel_idx in range(0, len(fuelbeds)):
        fuelbed_flaming = fuelbeds[fuel_idx]["emissions"]['flaming']
        fuelbed_smoldering = fuelbeds[fuel_idx]["emissions"]['smoldering']
        fuelbed_residual = fuelbeds[fuel_idx]["emissions"]['residual']
        for specie in select_species:
            if specie in fuelbed_flaming.keys():
                flaming[specie] += fuelbed_flaming[specie][0]
            if specie in fuelbed_smoldering.keys():
                smoldering[specie] += fuelbed_smoldering[specie][0]
            if specie in fuelbed_residual.keys():
                residual[specie] += fuelbed_residual[specie][0]

    # generate flaming smoldering residual emission array
    flaming_arry = []
    smoldering_arry = []
    residual_arry = []
    for select_specie in select_species:
        flaming_arry.append(flaming[select_specie])
        smoldering_arry.append(smoldering[select_specie])
        residual_arry.append(residual[select_specie])
    flaming_arry = np.array(flaming_arry)
    smoldering_arry = np.array(smoldering_arry)
    residual_arry = np.array(residual_arry)
    return {"flaming_emission": flaming_arry, "smoldering_emission": smoldering_arry, "residual_emission": residual_arry}


def findSpatialIndex(fire_x, fire_y, X_ctr, Y_ctr):
    """

    :param fire_x: X of fire location in CMAQ projection
    :param fire_y: Y of fire location in CMAQ projection
    :param X_ctr: CMAQ grid X center
    :param Y_ctr: CMAQ grid Y center
    :return: x_idx, y_idx which are the fire location in CMAQ grid
    """
    dist = np.sqrt((X_ctr - fire_x) ** 2 + (Y_ctr - fire_y) ** 2)
    x_idx, y_idx = np.unravel_index(np.argmin(dist, axis=None), dist.shape)
    return x_idx, y_idx


def dailyEmission(mcip_gridcro2d, bsp_filename):
    """

    :param mcip_gridcro2d: CMAQ MCIP cro2d output
    :param bsp_filename: BlueSKY daily output
    :return: a daily emission tensor (species, CMAQ_X_length, CMAQ_Y_length)
    (notice in Southeastern US, we could have case which emission at 24:00 (next day))
    """
    # Unit tons/hour
    select_species = ["CO", "SO2", "NH3", "NOx", "PM10", "PM2.5", "VOC"]

    cmaq_2d_info = CMAQGrid2D(mcip_gridcro2d)
    # CMAQ grid definition
    crs = cmaq_2d_info["crs"]
    x_min = cmaq_2d_info["X_bdry"][0]
    x_max = cmaq_2d_info["X_bdry"][1]
    y_min = cmaq_2d_info["Y_bdry"][0]
    y_max = cmaq_2d_info["Y_bdry"][1]
    Xcenters = cmaq_2d_info["X_ctr"]
    Ycenters = cmaq_2d_info["Y_ctr"]

    # read fire data
    with open(bsp_filename) as jsfile:
        bluesky_data = json.load(jsfile)
    # hourly data (0 - 24 hr)
    # Because if a fire end at 18hr and UTC = -6, we will have an end time at 24 (CMAQ uses 25 hour emissions)
    emission_tensor = np.zeros((len(select_species), 25, Xcenters.shape[0], Xcenters.shape[1]))

    bsp_fires = bluesky_data["fires"]
    for bsp_fire in bsp_fires:
        lat = bsp_fire["activity"][0]['active_areas'][0]["specified_points"][0]["lat"]
        lon = bsp_fire["activity"][0]['active_areas'][0]["specified_points"][0]["lng"]
        fire_id = bsp_fire["id"]
        time_profile = bsp_fire["activity"][0]["active_areas"][0]["timeprofile"]
        area_acres = bsp_fire["activity"][0]['active_areas'][0]["specified_points"][0]["area"]
        fuelbeds = bsp_fire["activity"][0]['active_areas'][0]["specified_points"][0]["fuelbeds"]
        emission = bsp_fire["activity"][0]['active_areas'][0]["specified_points"][0]["emissions"]["summary"]
        utc_offset = bsp_fire["activity"][0]['active_areas'][0]["utc_offset"]

        # whether in grid boundary
        fire_x, fire_y = crs(lon, lat)
        if x_min <= fire_x <= x_max and y_min <= fire_y <= y_max:
            # temporal fraction
            hourly_frac = hourlyFraction(time_profile, utc_offset)
            flaming_hourly_frac = hourly_frac["flaming_hourly_frac"]
            smoldering_hourly_frac = hourly_frac["smoldering_hourly_frac"]
            residual_hourly_farc = hourly_frac["residual_hourly_farc"]
            # generate flaming smoldering residual emission array, the array is ordered by species array
            classified_emission = classifiedEmission(fuelbeds, select_species)
            flaming_arry = classified_emission["flaming_emission"]
            smoldering_arry = classified_emission["smoldering_emission"]
            residual_arry = classified_emission["residual_emission"]
            # generate emission matrix (species, time_period)
            emission_matrix = np.zeros((len(select_species), 25))
            for i in range(0, 25):
                emission_matrix[:, i] = flaming_hourly_frac[i] * flaming_arry + \
                                        smoldering_hourly_frac[i] * smoldering_arry + \
                                        residual_hourly_farc[i] * residual_arry
            # Find the index of fire point in grid
            x_idx, y_idx = findSpatialIndex(fire_x, fire_y, Xcenters, Ycenters)
            emission_tensor[:, :, x_idx, y_idx] += emission_matrix
        else:
            continue

    # daily
    emission_tensor_daily = np.sum(emission_tensor, axis=1)
    return emission_tensor_daily


def eventEmission(bsp_filename):
    """

    :param bsp_filename: blueSKY output
    :return: return a dataframe matrix [FIREID,AREA,DAY,LATI,LONGI,selected_species]
    """
    # Unit tons/hour
    select_species = ["CO", "SO2", "NH3", "NOx", "PM10", "PM2.5", "VOC"]
    # read fire data
    with open(bsp_filename) as jsfile:
        bluesky_data = json.load(jsfile)
    # TODO: Consult with Talat or Yongtao
    gas_species = {"CO": 28.01, "SO2": 64.066, "NH3": 17.031, "NOx": 46}

    bsp_fires = bluesky_data["fires"]
    data_frame_title = ["FIREID", "AREA", "DAY", "LATI", "LONGI"]
    data_frame_title.extend(select_species)
    records = []
    for bsp_fire in bsp_fires:
        lat = bsp_fire["activity"][0]['active_areas'][0]["specified_points"][0]["lat"]
        lon = bsp_fire["activity"][0]['active_areas'][0]["specified_points"][0]["lng"]
        fire_id = bsp_fire["id"]
        time_profile = bsp_fire["activity"][0]["active_areas"][0]["timeprofile"]
        area_acres = bsp_fire["activity"][0]['active_areas'][0]["specified_points"][0]["area"]
        emission = bsp_fire["activity"][0]['active_areas'][0]["specified_points"][0]["emissions"]["summary"]
        ignition_start = bsp_fire["activity"][0]['active_areas'][0]["ignition_start"]
        ignition_start = datetime.strptime(ignition_start, '%Y-%m-%dT%H:%M:%S')
        date = ignition_start.strftime("%Y-%m-%d")
        record = [fire_id, area_acres, date, lat, lon]
        for specie in select_species:
            if specie in emission.keys():
                # unit convert
                if specie in gas_species.keys():
                    emiss_tmp = tons_to_mole(emission[specie], gas_species[specie])
                else:
                    emiss_tmp = tons_to_kg(emission[specie])
                record.append(emiss_tmp)
            else:
                record.append(0)
        records.append(record)
    emission_df = pd.DataFrame(records, columns=data_frame_title)
    return emission_df


def verticalHourlyEmission(metcros3d, bsp_filename):
    """

    :param metcros3d: MCIP 3D Grid Information
    :param bsp_filename: BlueSKY output
    :return: a emission tensor (species, MCIP time length, LAY, MCIP X length, MCIP Y length)
    """
    # Unit tons/hour
    select_species = ["CO", "SO2", "NH3", "NOx", "PM10", "PM2.5", "VOC"]

    cmaq_3d_info = CMAQGrid3D(metcros3d)
    # CMAQ grid definition
    crs = cmaq_3d_info["crs"]
    x_min = cmaq_3d_info["X_bdry"][0]
    x_max = cmaq_3d_info["X_bdry"][1]
    y_min = cmaq_3d_info["Y_bdry"][0]
    y_max = cmaq_3d_info["Y_bdry"][1]
    Xcenters = cmaq_3d_info["X_ctr"]
    Ycenters = cmaq_3d_info["Y_ctr"]
    mcip_time = cmaq_3d_info["time"]
    mcip_height = cmaq_3d_info["height"]
    LAY = mcip_height.shape[1]
    # read fire data
    with open(bsp_filename) as jsfile:
        bluesky_data = json.load(jsfile)

    bsp_fires = bluesky_data["fires"]
    # species, time, layer, x, y
    emission_tensor = np.zeros((len(select_species), len(mcip_time), LAY, Xcenters.shape[0], Xcenters.shape[1]))
    for bsp_fire in bsp_fires:
        lat = bsp_fire["activity"][0]['active_areas'][0]["specified_points"][0]["lat"]
        lon = bsp_fire["activity"][0]['active_areas'][0]["specified_points"][0]["lng"]
        fire_id = bsp_fire["id"]
        time_profile = bsp_fire["activity"][0]["active_areas"][0]["timeprofile"]
        area_acres = bsp_fire["activity"][0]['active_areas'][0]["specified_points"][0]["area"]
        fuelbeds = bsp_fire["activity"][0]['active_areas'][0]["specified_points"][0]["fuelbeds"]
        emission = bsp_fire["activity"][0]['active_areas'][0]["specified_points"][0]["emissions"]["summary"]
        utc_offset = bsp_fire["activity"][0]['active_areas'][0]["utc_offset"]
        plumerise = bsp_fire["activity"][0]['active_areas'][0]["specified_points"][0]["plumerise"]

        # whether in grid boundary
        fire_x, fire_y = crs(lon, lat)
        if x_min <= fire_x <= x_max and y_min <= fire_y <= y_max:
            # Find the index of fire point in grid
            x_idx, y_idx = findSpatialIndex(fire_x, fire_y, Xcenters, Ycenters)
            mcip_loc_height = mcip_height[:, :, x_idx, y_idx]
            # get fraction of each phase, fraction definition : temporal fraction * height fraction
            emission_frac = verticalHourlyFraction(time_profile, plumerise, utc_offset, mcip_time, mcip_loc_height)
            flaming_hourly_frac = emission_frac["flaming_hourly_frac"]
            smoldering_hourly_frac = emission_frac["smoldering_hourly_frac"]
            residual_hourly_farc = emission_frac["residual_hourly_farc"]
            t_length, h_length = flaming_hourly_frac.shape
            # generate flaming smoldering residual emission array, the array is ordered by species array
            classified_emission = classifiedEmission(fuelbeds, select_species)
            flaming_arry = classified_emission["flaming_emission"]
            smoldering_arry = classified_emission["smoldering_emission"]
            residual_arry = classified_emission["residual_emission"]
            # generate emission matrix (species, time_period, layer)
            emission_matrix = np.zeros((len(select_species), t_length, h_length))
            for i in range(0, len(select_species)):
                emission_matrix[i, :, :] = flaming_hourly_frac * flaming_arry[i] + \
                                        smoldering_hourly_frac * smoldering_arry[i] + \
                                        residual_hourly_farc * residual_arry[i]
            emission_tensor[:, :, :, x_idx, y_idx] += emission_matrix
        else:
            continue
    return emission_tensor


def dailyEmissionSE(mcip_gridcro2d, bsp_filename):
    """

    :param mcip_gridcro2d: CMAQ MCIP cro2d output
    :param bsp_filename: BlueSKY daily output
    :return: a daily emission tensor (species, CMAQ_X_length, CMAQ_Y_length)
    (notice in Southeastern US, we could have case which emission at 24:00 (next day))
    """
    # Unit tons/hour
    select_species = ["CO", "SO2", "NH3", "NOx", "PM10", "PM2.5", "VOC"]

    cmaq_2d_info = CMAQGrid2D(mcip_gridcro2d)
    # CMAQ grid definition
    crs = cmaq_2d_info["crs"]
    Xcenters, Ycenters = CMAQGrid(-74.5, -95.5, 41, 24, mcip_gridcro2d)
    x_min = np.min(Xcenters) - 2000
    x_max = np.max(Xcenters) + 2000
    y_min = np.min(Ycenters) - 2000
    y_max = np.max(Ycenters) + 2000

    # read fire data
    with open(bsp_filename) as jsfile:
        bluesky_data = json.load(jsfile)
    # hourly data (0 - 24 hr)
    # Because if a fire end at 18hr and UTC = -6, we will have an end time at 24 (CMAQ uses 25 hour emissions)
    emission_tensor = np.zeros((len(select_species), 25, Xcenters.shape[0], Xcenters.shape[1]))

    bsp_fires = bluesky_data["fires"]
    for bsp_fire in bsp_fires:
        lat = bsp_fire["activity"][0]['active_areas'][0]["specified_points"][0]["lat"]
        lon = bsp_fire["activity"][0]['active_areas'][0]["specified_points"][0]["lng"]
        fire_id = bsp_fire["id"]
        time_profile = bsp_fire["activity"][0]["active_areas"][0]["timeprofile"]
        area_acres = bsp_fire["activity"][0]['active_areas'][0]["specified_points"][0]["area"]
        fuelbeds = bsp_fire["activity"][0]['active_areas'][0]["specified_points"][0]["fuelbeds"]
        emission = bsp_fire["activity"][0]['active_areas'][0]["specified_points"][0]["emissions"]["summary"]
        utc_offset = bsp_fire["activity"][0]['active_areas'][0]["utc_offset"]

        # whether in grid boundary
        fire_x, fire_y = crs(lon, lat)
        if x_min <= fire_x <= x_max and y_min <= fire_y <= y_max:
            # temporal fraction
            hourly_frac = hourlyFraction(time_profile, utc_offset)
            flaming_hourly_frac = hourly_frac["flaming_hourly_frac"]
            smoldering_hourly_frac = hourly_frac["smoldering_hourly_frac"]
            residual_hourly_farc = hourly_frac["residual_hourly_farc"]
            # generate flaming smoldering residual emission array, the array is ordered by species array
            classified_emission = classifiedEmission(fuelbeds, select_species)
            flaming_arry = classified_emission["flaming_emission"]
            smoldering_arry = classified_emission["smoldering_emission"]
            residual_arry = classified_emission["residual_emission"]
            # generate emission matrix (species, time_period)
            emission_matrix = np.zeros((len(select_species), 25))
            for i in range(0, 25):
                emission_matrix[:, i] = flaming_hourly_frac[i] * flaming_arry + \
                                        smoldering_hourly_frac[i] * smoldering_arry + \
                                        residual_hourly_farc[i] * residual_arry
            # Find the index of fire point in grid
            x_idx, y_idx = findSpatialIndex(fire_x, fire_y, Xcenters, Ycenters)
            emission_tensor[:, :, x_idx, y_idx] += emission_matrix
        else:
            continue

    # daily
    emission_tensor_daily = np.sum(emission_tensor, axis=1)
    return emission_tensor_daily


def eventEmissionPMC(bsp_filename):
    """

    :param bsp_filename: blueSKY output
    :return: return a dataframe matrix [FIREID,AREA,DAY,LATI,LONGI,selected_species]
    """
    # Unit tons/hour
    select_species = ["PM10", "PM2.5"]
    # read fire data
    with open(bsp_filename) as jsfile:
        bluesky_data = json.load(jsfile)
    # TODO: Consult with Talat or Yongtao
    gas_species = {"CO": 28.01, "SO2": 64.066, "NH3": 17.031, "NOx": 46}

    bsp_fires = bluesky_data["fires"]
    data_frame_title = ["FIREID", "AREA", "DAY", "LATI", "LONGI"]
    data_frame_title.extend(select_species)
    records = []
    for bsp_fire in bsp_fires:
        lat = bsp_fire["activity"][0]['active_areas'][0]["specified_points"][0]["lat"]
        lon = bsp_fire["activity"][0]['active_areas'][0]["specified_points"][0]["lng"]
        fire_id = bsp_fire["id"]
        fuelbeds = bsp_fire["activity"][0]['active_areas'][0]["specified_points"][0]["fuelbeds"]
        time_profile = bsp_fire["activity"][0]["active_areas"][0]["timeprofile"]
        area_acres = bsp_fire["activity"][0]['active_areas'][0]["specified_points"][0]["area"]
        emission = bsp_fire["activity"][0]['active_areas'][0]["specified_points"][0]["emissions"]["summary"]
        ignition_start = bsp_fire["activity"][0]['active_areas'][0]["ignition_start"]
        ignition_start = datetime.strptime(ignition_start, '%Y-%m-%dT%H:%M:%S')
        date = ignition_start.strftime("%Y-%m-%d")
        record = [fire_id, area_acres, date, lat, lon]
        PMC = 0
        for specie in select_species:
            if specie in emission.keys():
                # unit convert
                if specie in gas_species.keys():
                    emiss_tmp = tons_to_mole(emission[specie], gas_species[specie])
                else:
                    emiss_tmp = tons_to_kg(emission[specie])
                record.append(emiss_tmp)
            else:
                emiss_tmp = 0
                record.append(emiss_tmp)
            if specie == "PM10":
                PMC = emiss_tmp
            if specie == "PM2.5":
                PMC = PMC - emiss_tmp
        if PMC < 0:
            records.append(record)
    emission_df = pd.DataFrame(records, columns=data_frame_title)
    return emission_df