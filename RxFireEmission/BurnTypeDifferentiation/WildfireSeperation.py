import pandas as pd
from util.CompareHelper import pairwise_dist
import numpy as np
from datetime import datetime, timedelta
import pyproj
import queue


def seperate_wildfires(finn_df, spatial_threshold=1000, temporal_threshold=800):
    # Add X and Y
    sat_x = np.array([])
    sat_y = np.array([])
    sat_lon = finn_df["LONGI"]
    sat_lat = finn_df["LATI"]
    # Convert lat, lon to x, y and calculate distance
    p = pyproj.Proj("+proj=utm +zone=16N, +north +ellps=WGS84 +datum=WGS84 +units=m +no_defs")
    for i in range(0, len(sat_lon)):
        x_sat_tmp, y_sat_tmp = p(sat_lon[i], sat_lat[i], inverse=False)
        sat_x = np.append(sat_x, x_sat_tmp)
        sat_y = np.append(sat_y, y_sat_tmp)
    finn_df["X"] = sat_x
    finn_df["Y"] = sat_y
    # All dates in the file, sort from old day to latest day
    date = finn_df["DAY"]
    date_list = list(set(list(date)))
    date_list.sort()

    # Temporal tracking

    # Map records the results root: [children]
    root_children_map_res = {}
    # Map records parent and its root. It is used for new children to find their root.
    parent_root_map = {}
    for select_date in date_list:
        # Map records parent and its root. It is used for new children to find their root. This map is used to update
        # parent_root_map
        parent_root_map_tmp = {}

        next_date = select_date + timedelta(days=1)
        this_df = finn_df[finn_df["DAY"] == select_date]
        next_df = finn_df[finn_df["DAY"] == next_date]
        this_y = this_df["Y"].to_numpy().reshape(-1, 1)
        this_x = this_df["X"].to_numpy().reshape(-1, 1)
        this_id = this_df["FIREID"].to_numpy()
        next_y = next_df["Y"].to_numpy().reshape(-1, 1)
        next_x = next_df["X"].to_numpy().reshape(-1, 1)
        next_id = next_df["FIREID"].to_numpy()
        this_coord = np.hstack((this_x, this_y))
        next_coord = np.hstack((next_x, next_y))
        dist = pairwise_dist(next_coord, this_coord)
        for i in range(0, len(next_id)):
            # For each record in next day, find the potential parent in current day which
            # has the minimum distance with the record
            dist_next_id = dist[i, :]
            candidate_parent_id = this_id[np.argmin(dist_next_id)]
            if np.min(dist_next_id) <= temporal_threshold:
                # Whether parent fire is a root? If not, this_id will be a new root
                # Whether this_id in the parent_root_map, if in, get the root id and add
                # the next_id into the root_children_map_res array
                if candidate_parent_id in parent_root_map.keys():
                    root = parent_root_map[candidate_parent_id]
                    root_children_map_res[root].append(next_id[i])
                    parent_root_map_tmp[next_id[i]] = root
                else:
                    # This parent is a root, notice that there are two cases: 1. This root already has children
                    # 2. This root does not have any children yet
                    if candidate_parent_id in root_children_map_res.keys():
                        # Already has children
                        root_children_map_res[candidate_parent_id].append(next_id[i])
                    else:
                        # This root does not have any children yet
                        root_children_map_res[candidate_parent_id] = [next_id[i]]
                    # For these two cases, we need to record next day fires and their root.
                    # It will be used for next next day. It will be used for judge whether a parent is a root.
                    parent_root_map_tmp[next_id[i]] = candidate_parent_id
            else:
                continue

        parent_root_map = parent_root_map_tmp

    spatial_clustering = []
    for select_date in date_list:
        this_df = finn_df[finn_df["DAY"] == select_date]
        this_y = this_df["Y"].to_numpy().reshape(-1, 1)
        this_x = this_df["X"].to_numpy().reshape(-1, 1)
        this_id = this_df["FIREID"].to_numpy()
        coord = np.hstack((this_x, this_y))
        dist = pairwise_dist(coord, coord)
        N, _ = coord.shape
        select_flag = np.zeros(N, dtype=bool)
        dist_matrix = pairwise_dist(coord, coord)
        # cluster_number = 0
        for i in range(0, N):
            if not select_flag[i]:
                spatial_clustering_tmp = []
                temp_queue = queue.Queue()
                temp_queue.put(i)
                select_flag[i] = True
                while not temp_queue.empty():
                    select_point_idx = temp_queue.get()
                    spatial_clustering_tmp.append(this_id[select_point_idx])
                    dist_array = dist_matrix[select_point_idx, :]
                    # filter out the idx need to add to the queue
                    candidate_idx_flag = (dist_array <= spatial_threshold) & (~select_flag)
                    candidate_idx = np.where(candidate_idx_flag)[0]
                    for candidate_idx_tmp in candidate_idx:
                        temp_queue.put(candidate_idx_tmp)
                        select_flag[candidate_idx_tmp] = True
                spatial_clustering.append(spatial_clustering_tmp)
            else:
                continue

    # Map records the results root: [children]
    # root_children_map_res = {}
    # spatial_clustering: [[cluster_1], [cluster_2]]
    # Generate a dataframe (fireid, spatial (no temporal connected -1), temporal)
    # Notice the columns (spatial cluster id, temporal cluster id) is a bipartite graph edges, what we need to combine them
    # is by using graph algorithm to find connected clusters.
    spatial_cluster = []
    fire_id_spatial = []
    spatial_cluster_num = 0
    for i in range(0, len(spatial_clustering)):
        fire_id_spatial.extend(spatial_clustering[i])
        spatial_cluster_id = ["SP" + str(spatial_cluster_num)] * len(spatial_clustering[i])
        spatial_cluster.extend(spatial_cluster_id)
        spatial_cluster_num += 1

    spatial_fire = pd.DataFrame({"fire_id": fire_id_spatial, "spatial_cluster": spatial_cluster})

    temporal_cluster = []
    fire_id_temporal = []
    temporal_cluster_num = 0
    for key in root_children_map_res.keys():
        fire_id_temporal.append(key)
        fire_id_temporal.extend(root_children_map_res[key])
        temporal_cluster_id = ["TP" + str(temporal_cluster_num)] * (len(root_children_map_res[key]) + 1)
        temporal_cluster.extend(temporal_cluster_id)
        temporal_cluster_num += 1

    temporal_fire = pd.DataFrame({"fire_id": fire_id_temporal, "temporal_cluster": temporal_cluster})

    spatial_temporal_fire_all = spatial_fire.merge(temporal_fire, how='left', on='fire_id')

    # Do not care about isolated vertex in graph
    spatial_temporal_fire = spatial_temporal_fire_all.dropna()
    spatial_temporal_fire = spatial_temporal_fire.reset_index(drop=True)
    # fires which have temporal id are the fires we want to track, we start with these nodes and
    # traversal the bipartite graph
    # Generate edge map
    # temporal_to_spatial: {temporal_id: spatial_id}
    # spatial_to_temporal: {spatial_id: temporal_id}
    temporal_id_set = set(spatial_temporal_fire["temporal_cluster"].to_numpy())
    spatial_id_set = set(spatial_temporal_fire["spatial_cluster"].to_numpy())
    temporal_to_spatial = {}
    spatial_to_temporal = {}
    for temporal_id_set_tmp in temporal_id_set:
        spatial_cluster_connected = spatial_temporal_fire[spatial_temporal_fire["temporal_cluster"] == temporal_id_set_tmp]["spatial_cluster"]
        temporal_to_spatial[temporal_id_set_tmp] = list(set(spatial_cluster_connected.to_numpy()))

    for spatial_id_set_tmp in spatial_id_set:
        # No nan values in spatial
        temporal_cluster_connected = spatial_temporal_fire[spatial_temporal_fire["spatial_cluster"] == spatial_id_set_tmp]["temporal_cluster"]
        spatial_to_temporal[spatial_id_set_tmp] = list(set(temporal_cluster_connected.to_numpy()))

    cluster_result = {}
    searched_cluster = set()
    cluster_id = 0
    for key in temporal_to_spatial.keys():
        if key not in searched_cluster:
            tmp_queue = queue.Queue()
            tmp_queue.put(key)
            searched_cluster.add(key)
            candidate_cluster = None
            cluster_result[cluster_id] = []
            while not tmp_queue.empty():
                cluster_id_tmp = tmp_queue.get()
                cluster_result[cluster_id].append(cluster_id_tmp)

                if "TP" in cluster_id_tmp:
                    candidate_cluster = temporal_to_spatial[cluster_id_tmp]
                elif "SP" in cluster_id_tmp:
                    candidate_cluster = spatial_to_temporal[cluster_id_tmp]

                for candidate_cluster_tmp in candidate_cluster:
                    if candidate_cluster_tmp not in searched_cluster:
                        tmp_queue.put(candidate_cluster_tmp)
                        searched_cluster.add(candidate_cluster_tmp)
            cluster_id += 1
        else:
            continue

    # Add the cluster result to cluster_id in dataframe for spatial_temporal_fire_all
    spatial_temporal_fire_all["cluster_id"] = np.nan
    for key in cluster_result:
        for cluster_tmp in cluster_result[key]:
            if "TP" in cluster_tmp:
                spatial_temporal_fire_all.loc[spatial_temporal_fire_all["temporal_cluster"] == cluster_tmp, "cluster_id"] = "WILDFIRE" + str(key)
            elif "SP" in cluster_tmp:
                spatial_temporal_fire_all.loc[spatial_temporal_fire_all["spatial_cluster"] == cluster_tmp, "cluster_id"] = "WILDFIRE" + str(key)

    # Generate the wildfire data
    spatial_temporal_fire_all["FIREID"] = spatial_temporal_fire_all["fire_id"]
    res = finn_df.merge(spatial_temporal_fire_all[["FIREID", "cluster_id"]], how='left', on='FIREID')
    res = res[["FIREID", "AREA", "DAY", "LATI", "LONGI", "cluster_id"]]
    res = res.dropna()
    res = res.reset_index(drop=True)
    return res