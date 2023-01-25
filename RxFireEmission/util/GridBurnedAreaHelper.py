import pyproj
import netCDF4 as nc
import numpy as np
import math
from util.CompareHelper import pairwise_dist
import torch
import torch.nn.functional as F
from shapely.geometry import Point


def CMAQProj(mcip_gridcro2d):
    """

    :param mcip_gridcro2d: MCIP GRIDCRO2D file
    :return: return a projection (trans (lon, lat) -> X, Y), x, y = cmaq_proj(lon, lat)
    """
    ds = nc.Dataset(mcip_gridcro2d)
    lat_1 = ds.getncattr('P_ALP')
    lat_2 = ds.getncattr('P_BET')
    lat_0 = ds.getncattr('YCENT')
    lon_0 = ds.getncattr('XCENT')
    crs = pyproj.Proj("+proj=lcc +a=6370000.0 +b=6370000.0 +lat_1=" + str(lat_1)
                      + " +lat_2=" + str(lat_2) + " +lat_0=" + str(lat_0) +
                      " +lon_0=" + str(lon_0))
    return crs


def CMAQGrid(max_lon, min_lon, max_lat, min_lat, mcip_gridcro2d):
    cmaq_proj = CMAQProj(mcip_gridcro2d)
    ds = nc.Dataset(mcip_gridcro2d)
    xcell = ds.getncattr('XCELL')
    ycell = ds.getncattr('YCELL')
    xorig = ds.getncattr('XORIG')
    yorig = ds.getncattr('YORIG')
    # Find xorig, yorig by (min_lon, min_lat)
    x_min, x_max, y_min, y_max = None, None, None, None
    x_array = []
    y_array = []
    for lon_tmp in [max_lon, min_lon]:
        for lat_tmp in [max_lat, min_lat]:
            # print(cmaq_proj(lon_tmp, lat_tmp))
            x_tmp, y_tmp = cmaq_proj(lon_tmp, lat_tmp)
            x_array.append(x_tmp)
            y_array.append(y_tmp)
    x_min = np.min(x_array)
    y_min = np.min(y_array)
    x_max = np.max(x_array)
    y_max = np.max(y_array)
    if x_min < xorig:
        xorig = xorig - math.ceil((xorig - x_min)/xcell) * xcell
    if y_min < yorig:
        yorig = yorig - math.ceil((yorig - y_min)/ycell) * ycell
    # Based on XORIG and YORIG to generate all grids
    ncols = math.ceil((x_max - xorig)/xcell)
    nrows = math.ceil((y_max - yorig)/ycell)
    # print(ncols)
    # print(nrows)
    # > for X, Y cell centers
    x_center_range = np.linspace(xorig + xcell / 2, (xorig + xcell / 2) + xcell * (ncols - 1), ncols)
    y_center_range = np.linspace(yorig + ycell / 2, (yorig + ycell / 2) + ycell * (nrows - 1), nrows)
    x_centers, y_centers = np.meshgrid(x_center_range, y_center_range)
    return x_centers, y_centers



def GridMatching(coord, burned_area, grid_x_centers, grid_y_centers):
    """

    :param coord: Array data (n, 2) Use grid projection to transfer lat, lon to (x, y) coord
    :param burned_area: Array data (n, 1)
    :param grid_x_centers: Matrix data (m, p)
    :param grid_y_centers: Matrix data (m, p)
    :return: Burned Area for each grid (m, p)
    """
    m, p = grid_x_centers.shape
    grid_burned_area = np.zeros((m * p, 1))
    x_flat_ctr = np.reshape(grid_x_centers, (m * p, 1))
    y_flat_ctr = np.reshape(grid_y_centers, (m * p, 1))
    grid_coord = np.hstack((x_flat_ctr, y_flat_ctr))
    dist_matrix = pairwise_dist(grid_coord, coord)
    nearest_idx = np.argmin(dist_matrix, axis=0) # (n, 1)
    # Add the burned area to grid
    for i in range(0, len(burned_area)):
        burned_area_tmp = burned_area[i]
        matched_grid_idx = nearest_idx[i]
        grid_burned_area[matched_grid_idx] += burned_area_tmp
    # reshape the burned area
    return np.reshape(grid_burned_area, (m, p))


def FINNGridMatching(coord, burned_area, grid_x_centers, grid_y_centers, veg):
    """

    :param coord: Array data (n, 2) Use grid projection to transfer lat, lon to (x, y) coord
    :param burned_area: Array data (n, 1)
    :param grid_x_centers: Matrix data (m, p)
    :param grid_y_centers: Matrix data (m, p)
    :return: Burned Area for each grid (m, p)
    :param veg: vegetation type from MODIS: Array data (n, 1)
    :return: Burned Area for each grid each veg type (m, p, k) where k is the vegetation type (k=5 in SE case)
             SE veg type: {1, 2, 4, 6, 9}
    """
    veg_types = [1, 2, 4, 6, 9]
    m, p = grid_x_centers.shape
    k = len(veg_types)
    grid_burned_area = np.zeros((m * p, k))
    x_flat_ctr = np.reshape(grid_x_centers, (m * p, 1))
    y_flat_ctr = np.reshape(grid_y_centers, (m * p, 1))
    grid_coord = np.hstack((x_flat_ctr, y_flat_ctr))
    dist_matrix = pairwise_dist(grid_coord, coord)
    nearest_idx = np.argmin(dist_matrix, axis=0) # (n, 1)
    # Add the burned area to grid
    for i in range(0, len(burned_area)):
        burned_area_tmp = burned_area[i]
        matched_grid_idx = nearest_idx[i]
        matched_veg_type = veg[i]
        veg_index = -1
        try:
            veg_index = veg_types.index(matched_veg_type)
        except:
            print("Vegetation type does not exist: " + str(matched_veg_type))
            return
        grid_burned_area[matched_grid_idx, veg_index] += burned_area_tmp
    # reshape the burned area
    return np.reshape(grid_burned_area, (m, p, k))


def CountyMatching(coord, burned_area, polygons):
    """

    :param coord: Array data (n, 2) Use lat, lon coord
    :param burned_area: Array data (n, 1)
    :param polygons: Array of polygons (m, 1)
    :return: (m, 1) total burned area for each polygons (m, 1)
    """
    county_burned_area = np.zeros(len(polygons))
    n, _ = coord.shape
    for i in range(0, n):
        coord_tmp = coord[i, :]
        coord_point = Point(coord_tmp[0], coord_tmp[1])
        for polygon_idx in range(0, len(polygons)):
            if polygons[polygon_idx].contains(coord_point):
                county_burned_area[polygon_idx] += burned_area[i]
                break
    return county_burned_area


def sampling2D(grid_burned_area):
    kernel = np.ones((3, 3)) * (1/9)
    padded_grid_burned_area = np.pad(grid_burned_area, [(1, 1), (1, 1)], mode='constant', constant_values=0)
    result = np.zeros(grid_burned_area.shape)
    m, n = result.shape
    for i in range(0, m):
        for j in range(0, n):
            select_sub_area = padded_grid_burned_area[i: i+3, j:j+3]
            result[i, j] = np.sum(select_sub_area * kernel)
    return result


def sampling3D(grid_burned_area):
    t, m, n = grid_burned_area.shape
    result = np.zeros(grid_burned_area.shape)
    for i in range(0, t):
        grid_burned_area_2d = grid_burned_area[i, :, :]
        sampled_2d = sampling2D(grid_burned_area_2d)
        result[i, :, :] = sampled_2d
    return result


def sampling(grid_burned_area):
    kernel = np.ones((3, 3)) * (1 / 9)
    padded_grid_burned_area = np.pad(grid_burned_area, [(0, 0), (1, 1), (1, 1)], mode='constant', constant_values=0)
    result = np.zeros(grid_burned_area.shape)
    t, m, n = result.shape
    for i in range(0, m):
        for j in range(0, n):
            select_sub_area = padded_grid_burned_area[:, i: i+3, j:j+3]
            result[:, i, j] = np.sum(select_sub_area * kernel, axis=(1, 2))
    return result


def fastsampling(grid_burned_area):
    grid_burned_area_tmp = torch.from_numpy(grid_burned_area)
    t, m, n = grid_burned_area_tmp.shape
    grid_burned_area_tmp = grid_burned_area_tmp[:, None, :, :]
    kernel = np.ones((1, 3, 3)) * (1 / 9)
    filters = torch.from_numpy(kernel)
    filters = filters[:, None, :, :]
    res = F.conv2d(grid_burned_area_tmp, filters, padding=1)
    return np.squeeze(res.numpy())