from util import GeoHelper
import pandas as pd
from shapely import geometry


def extractByState(filename, output_name, state_name):
    state_polygon = GeoHelper.StatePolygon(state_name)
    df = pd.read_csv(filename)
    valid_idx = []
    for index, row in df.iterrows():
        lat = row['LATI']
        lon = row['LONGI']
        fire_point = geometry.Point(lon, lat)
        if state_polygon.contains(fire_point):
            valid_idx.append(index)
    res_df = df.iloc[valid_idx]
    res_df.to_csv(output_name, index=False)


def extracDataFrameByState(filename, state_name):
    state_polygon = GeoHelper.StatePolygon(state_name)
    df = pd.read_csv(filename)
    valid_idx = []
    for index, row in df.iterrows():
        lat = row['LATI']
        lon = row['LONGI']
        fire_point = geometry.Point(lon, lat)
        if state_polygon.contains(fire_point):
            valid_idx.append(index)
    res_df = df.iloc[valid_idx]
    res_df = res_df.reset_index()
    return res_df


def removeFederalLandFires(filename, output_name, state_name):
    federal_lands = GeoHelper.FederalLand(state_name)
    df = pd.read_csv(filename)
    valid_idx = []
    for index, row in df.iterrows():
        lat = row['LATI']
        lon = row['LONGI']
        fire_point = geometry.Point(lon, lat)
        valid_flag = True
        for federal_land in federal_lands:
            if federal_land.contains(fire_point):
                valid_flag = False
                break
        if valid_flag:
            valid_idx.append(index)
    res_df = df.iloc[valid_idx]
    res_df.to_csv(output_name, index=False)