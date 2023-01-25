import numpy as np
import pandas as pd


def pairwise_dist(x, y):
    """

    :param x: N * 2 array (N data points, (lon, lat) dimensions)
    :param y: M * 2 array (M data points, (lon, lat) dimensions)
    :return: N x M array, where dist2[i, j] is the euclidean distance between x[i, :] and y[j, :]
    """
    diff = x[:, :, None] - y[:, :, None].T
    distance = np.sqrt(np.sum(diff * diff, axis=1))
    return distance


def pairwise_burn_diff(burn_x, burn_y):
    """

    :param burn_x: (N,) array
    :param burn_y: (M,) array
    :return: N x M array, where diff[i, j] is the absolute distance between burn_x[i] and burn_y[j]
    """
    diff = burn_x[:, None] - burn_y[:, None].T
    abs_diff = np.abs(diff)
    return abs_diff


def thetaFunc(diff_abs, dh):
    diff = diff_abs - dh
    return sum(diff > 0)


def sumByFireID(finn_df):
    finn_df = finn_df[['DAY', 'POLYID', 'FIREID', 'GENVEG', 'LATI', 'LONGI', 'AREA']]
    area = finn_df.groupby(['FIREID'])["AREA"].sum() * 0.000247105
    finn_df = finn_df.drop_duplicates(subset=['FIREID'])
    # Helper DF
    df_tmp = pd.DataFrame(columns=("FIREID", "AREA"))
    df_tmp["FIREID"] = area.index
    df_tmp["AREA"] = area.values
    # Same data type for key
    df_tmp["FIREID"] = df_tmp["FIREID"].astype(int)
    finn_df["FIREID"] = finn_df["FIREID"].astype(int)
    # LEFT JOIN
    finn_df = pd.merge(df_tmp, finn_df[['DAY', 'POLYID', 'FIREID', 'GENVEG', 'LATI', 'LONGI']], how="left", on=["FIREID"])
    # RESET IDX
    finn_df = finn_df.reset_index(drop=True)
    return finn_df


def removeDuplicateRecord(record_df):
    record_df = record_df.drop_duplicates()
    record_df = record_df.reset_index(drop=True)
    if len(np.unique(record_df["Id"])) != len(record_df):
        print("Duplicate")
    return record_df


def findDuplicate(id_list):
    id_dict = {}
    duplicate = []
    for i in range(0, len(id_list)):
        if id_list[i] in id_dict.keys():
            id_dict[id_list[i]] += 1
            duplicate.append(id_list[i])
        else:
            id_dict[id_list[i]] = 1
    print(duplicate)


def penalty_score(x, y):
    """

    :param x: N * k array (N data points, (lon, lat) dimensions)
    :param y: M * k array (N data points, (lon, lat) dimensions)
    :return: N x M array, where dist2[i, j] is the euclidean distance between x[i, :] and y[j, :]
    """
    # Normalize firstly
    coord_x = x[:, 0: 2]
    coord_y = y[:, 0: 2]
    diff = coord_x[:, :, None] - coord_y[:, :, None].T
    distance = np.sqrt(np.sum(diff * diff, axis=1))

    feature_x = x[:, 2:]
    feature_y = y[:, 2:]
    diff = feature_x[:, :, None] - feature_y[:, :, None].T
    feature_distance = np.sqrt(np.sum(diff * diff, axis=1))

    # Normalize the distance
    distance = (distance - np.mean(distance, axis=1).reshape(-1, 1))/np.std(distance, axis=1).reshape(-1, 1)
    feature_distance = (feature_distance - np.mean(feature_distance, axis=1).reshape(-1, 1))/np.std(feature_distance, axis=1).reshape(-1, 1)
    res_dist = np.sqrt(distance ** 2 + feature_distance ** 2)
    return res_dist