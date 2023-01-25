import os
import rasterio
import pyproj
import numpy as np
from util.CompareHelper import pairwise_dist
from rasterio.enums import Resampling
from collections import defaultdict


def nlcdData(nlcd_dir, bbox):
    # return a lat, lon matrix, nlcd_data matrix and a map for category meaning
    # Reference: Author: Joshua Hrisko
    nlcd_files = [ii for ii in os.listdir(nlcd_dir) if ii[0] != '.']
    nlcd_filename = [ii for ii in nlcd_files if ii.endswith('.img')][0]
    legend = np.array([0, 11, 12, 21, 22, 23, 24, 31, 41, 42, 43, 51, 52, 71, 72, 73, 74, 81, 82, 90, 95])
    leg_str = np.array(
        ['No Data', 'Open Water', 'Perennial Ice/Snow', 'Developed, Open Space', 'Developed, Low Intensity',
         'Developed, Medium Intensity', 'Developed High Intensity', 'Barren Land (Rock/Sand/Clay)',
         'Deciduous Forest', 'Evergreen Forest', 'Mixed Forest', 'Dwarf Scrub', 'Shrub/Scrub',
         'Grassland/Herbaceous', 'Sedge/Herbaceous', 'Lichens', 'Moss', 'Pasture/Hay', 'Cultivated Crops',
         'Woody Wetlands', 'Emergent Herbaceous Wetlands'])
    # generate map
    legend_map = {}
    idx = 0
    for leg_value in legend:
        legend_map[leg_value] = leg_str[idx]
        idx += 1
    # colormap determination and setting bounds
    with rasterio.open(nlcd_dir+nlcd_filename) as r:
        try:
            oviews = r.overviews(1) # list of overviews from biggest to smallest
            oview = oviews[4] # we grab a smaller view, since we're plotting the entire USA
            print('Decimation factor= {}'.format(oview))
            # NOTE this is using a 'decimated read' (http://rasterio.readthedocs.io/en/latest/topics/resampling.html)
            nlcd = r.read(1, out_shape=(1, int(r.height // oview), int(r.width // oview)), resampling=Resampling.mode)

            # Or if you see an interesting feature and want to know the spatial coordinates:
            row,col = np.meshgrid(np.arange(0,r.height-(oview),oview),np.arange(0,r.width-oview,oview))
            east, north = r.xy(row,col) # image --> spatial coordinates
            east = np.ravel(east); north = np.ravel(north) # collapse coordinates for efficient transformation

            tfm = pyproj.transformer.Transformer.from_crs(r.crs, 'epsg:4326') # transform for raster image coords to lat/lon
            lat, lon = tfm.transform(east, north) # transform the image coordinates
            y = np.reshape(north, np.shape(row))
            x = np.reshape(east, np.shape(col))
            lons = np.reshape(lon, np.shape(row)) # reshape to grid
            lats = np.reshape(lat, np.shape(col)) # reshape to grid
        except:
            print('FAILURE')
    print("Resolution is: " + str(x[1, 0] - x[0, 0]) + " m")
    nlcd = np.transpose(nlcd)
    x_l_id_arry = []
    x_r_idx_arry = []
    for i in range(0, lats.shape[0]):
        x_l_idx_cur = np.argmin(lats[i, :] >= bbox[-1]) - 1
        x_r_idx_cur = np.argmax(lats[i, :] <= bbox[1]) + 1
        x_l_id_arry.append(x_l_idx_cur)
        x_r_idx_arry.append(x_r_idx_cur)
    x_l_idx = np.min(x_l_id_arry)
    x_r_idx = np.max(x_r_idx_arry)

    y_u_idx_arry = []
    y_l_idx_arry = []
    for i in range(0, lons.shape[1]):
        y_u_idx_cur = np.argmin(lons[:, i] <= bbox[2]) + 1
        y_l_idx_cur = np.argmax(lons[:, i] >= bbox[0]) - 1
        y_u_idx_arry.append(y_u_idx_cur)
        y_l_idx_arry.append(y_l_idx_cur)
    y_l_idx = np.min(y_l_idx_arry)
    y_u_idx = np.max(y_u_idx_arry)
    # sliced data
    lats = lats[y_l_idx: y_u_idx, x_l_idx: x_r_idx]
    lons = lons[y_l_idx: y_u_idx, x_l_idx: x_r_idx]
    nlcd = nlcd[y_l_idx: y_u_idx, x_l_idx: x_r_idx]
    return lats, lons, nlcd, legend_map


def add_nlcd_attr(record_lon, record_lat, nlcd_lons, nlcd_lats, nlcd_data):
    record_lon = record_lon.reshape((-1, 1))
    record_lat = record_lat.reshape((-1, 1))
    record_coord = np.hstack((record_lon, record_lat))
    nlcd_lons_flat = nlcd_lons.reshape((-1, 1))
    nlcd_lats_flat = nlcd_lats.reshape((-1, 1))
    nlcd_data_flat = nlcd_data.reshape((-1, 1))
    nlcd_coord = np.hstack((nlcd_lons_flat, nlcd_lats_flat))
    dist_matrix = pairwise_dist(record_coord, nlcd_coord)
    grid_index = np.argmin(dist_matrix, axis=1)
    nlcd_data_res = nlcd_data_flat[grid_index]
    return nlcd_data_res


def counts(x):
    # We'll ignore the mask (i.e. consider partial cells) if
    # configured to do so or if the mask is all true values
    # (i.e. all cells are partial)
    counts = defaultdict(lambda: 0)
    for i in range(len(x.data)):
        for j in range(len(x.data[i])):
            # print(x.data[i][j])
            counts[x.data[i][j]] += 1
    return dict(counts)


def max_counts(counts_dict):
    max_num = 0
    max_type = 0
    for key in counts_dict.keys():
        if counts_dict[key] >= max_num:
            max_num = counts_dict[key]
            max_type = key
    return max_type