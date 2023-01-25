from datetime import datetime
import numpy as np
import fiona
from shapely.geometry import shape, Point


def generateFire(fire_id, lat, lon, time, area, state):
    fire_dict = {"id": fire_id,
                 "type": "rx",
                 "fuel_type": "natural",
                 "activity": [
                     {
                         "active_areas": [
                             {
                                 #TODO: Maybe not true for some southeastern states
                                 "utc_offset": "-05:00",
                                 "start": datetime.strftime(time, "%Y-%m-%d") + "T09:00:00",
                                 "end": datetime.strftime(time, "%Y-%m-%d") + "T15:00:00",
                                 "ignition_start": datetime.strftime(time, "%Y-%m-%d") + "T09:00:00",
                                 "ignition_end": datetime.strftime(time, "%Y-%m-%d") + "T15:00:00",
                                 "country": "USA",
                                 "state": state,
                                 "ecoregion": "southern",
                                 "specified_points":[
                                     {
                                         "lat": lat,
                                         "lng": lon,
                                         "area": area
                                     }
                                 ]
                             }
                         ]
                     }
                 ]}
    return fire_dict


def readBlueSkyEmission(select_species, json_obj):
    emission_matrix = np.zeros((len(json_obj["fires"]), len(select_species)))
    emission_matrix[:] = np.nan
    fire_ids = []
    for i in range(0, len(json_obj["fires"])):
        emission_dict = json_obj["fires"][i]["emissions"]["summary"]
        fire_id = json_obj["fires"][i]["id"]
        fire_ids.append(fire_id)
        for j in range(0, len(select_species)):
            current_specie = select_species[j]
            emission_matrix[i, j] = emission_dict[current_specie]
    fire_ids = np.array(fire_ids).reshape(-1, 1)
    res = np.hstack((fire_ids, emission_matrix))
    return res


def generateFirePlumerise(fire_id, lat, lon, time, area, state):
    # calculate duration
    if area <= 10:
        duration = 2
    elif area > 10 and area <= 30:
        duration = 3
    elif area > 30 and area <= 70:
        duration = 4
    elif area > 70 and area <= 150:
        duration = 5
    elif area > 150 and area <= 300:
        duration = 6
    else:
        duration = 7
    # generate the end time str
    start_time_hour = 11
    end_time_hour = start_time_hour + duration
    # calculate utc
    utc_offset = utc_zone(lon, lat)
    fire_dict = {"id": fire_id,
                 "type": "rx",
                 "fuel_type": "natural",
                 "activity": [
                     {
                         "active_areas": [
                             {
                                 "utc_offset": utc_offset,
                                 "start": datetime.strftime(time, "%Y-%m-%d") + "T11:00:00",
                                 "end": datetime.strftime(time, "%Y-%m-%d") + "T" + str(end_time_hour) + ":00:00",
                                 "ignition_start": datetime.strftime(time, "%Y-%m-%d") + "T11:00:00",
                                 "ignition_end": datetime.strftime(time, "%Y-%m-%d") + "T" + str(end_time_hour) + ":00:00",
                                 "country": "USA",
                                 "state": state,
                                 "ecoregion": "southern",
                                 "specified_points":[
                                     {
                                         "lat": lat,
                                         "lng": lon,
                                         "area": area
                                     }
                                 ]
                             }
                         ]
                     }
                 ]}
    return fire_dict


def generateMetInfo(met_dir, time):
    filename = met_dir + datetime.strftime(time, "%Y%m%d") + "_nam12"
    file = {"file": filename,
            "first_hour": datetime.strftime(time, "%Y-%m-%d") + "T00:00:00",
            "last_hour": datetime.strftime(time, "%Y-%m-%d") + "T23:00:00"}
    files = [file]
    res_dict = {"files": files}
    return res_dict


def utc_zone(lon, lat):
    utc_file = "/Users/zongrunli/Desktop/RxFireEmission/data/timezone/timezone.shp"
    utc_zones = fiona.open(utc_file)
    fire_point = Point(lon, lat)
    zone_value_res = None
    for utc_zone in utc_zones:
        zone_value = utc_zone['properties']['ZONE']
        zone_geo = shape(utc_zone['geometry'])
        if zone_geo.contains(fire_point):
            zone_value_res = zone_value
            break
    # convert zone value to str
    if zone_value_res < 0:
        zone_value_res_pos = -zone_value_res
        hour_num = int(zone_value_res_pos)
        minute_num = int((zone_value_res_pos - hour_num) * 60)
        res = "-" + str(hour_num).rjust(2, '0') + ":" + str(minute_num).rjust(2, '0')
    else:
        hour_num = int(zone_value_res)
        minute_num = int((zone_value_res - hour_num) * 60)
        res = "+" + str(hour_num).rjust(2, '0') + ":" + str(minute_num).rjust(2, '0')
    return res