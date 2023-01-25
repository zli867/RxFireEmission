import pandas as pd
import requests
import json
import numpy as np
import shapefile as shp
from shapely.geometry import Point
from shapely.geometry.polygon import Polygon


def ConvertToCsv(filename, output_filename, *columns):
    df = pd.DataFrame(pd.read_excel(filename))
    column_list = []
    # Select the column
    for column in columns:
        column_list.append(column)
    df = df[column_list]
    # Write the dataframe object into csv file
    df.to_csv(output_filename, index=None, header=True)


def DeleteInvalidData(filename, *columns_not_nan):
    df = pd.read_csv(filename)
    delete_number = 0
    removed_index = []
    for row in df.iterrows():
        index = row[0]
        invalid = False
        invalid_column = ""
        for column in columns_not_nan:
            invalid = invalid or pd.isna(df.iloc[index].at[column])
            if invalid:
                invalid_column = column
                break
        if invalid:
            print("id: " + str(df.iloc[index].at["id"]) + " Invalid column: " + invalid_column)
            removed_index.append(index)
            delete_number += 1
        else:
            continue
    df.drop(removed_index, inplace=True)
    # Write the dataframe object into csv file
    df.to_csv(filename, index=None, header=True)
    print("There are " + str(delete_number) + " invalid records")
    print("New file is Written!")


def DeleteDeniedBurn(filename):
    df = pd.read_csv(filename)
    approval = df["Approval"]
    removed_index = []
    for i in range(0, len(approval)):
        if approval[i] != "Approved":
            print("The Status of " + str(df.iloc[i].at["id"]) + ": " + approval[i])
            removed_index.append(i)
    df.drop(removed_index, inplace=True)
    delete_number = len(removed_index)
    # Write the dataframe object into csv file
    df.to_csv(filename, index=None, header=True)
    print("There are " + str(delete_number) + " invalid records")
    print("New file is Written!")


def WriteSameAdrress(filename):
    df = pd.read_csv(filename)
    address = df['BurnAddress'].astype(str)
    same_address_number = 0
    for i in range(0, len(address)):
        address_tmp = str(address[i])
        address_tmp = address_tmp.lower()
        if address_tmp.find("same") != -1:
            # Find the nearest not "the same as" address
            start_search_index = i - 1
            replace_address = ""
            while start_search_index >= 0:
                search_address = address[start_search_index].lower()
                if search_address.find("same") == -1:
                    replace_address = address[start_search_index]
                    break
                else:
                    start_search_index = start_search_index - 1
            df.loc[i, 'BurnAddress'] = replace_address
            print("id: " + str(df.loc[i, 'id']) + " has the same as address.")
            same_address_number += 1
    print("Replaced " + str(same_address_number) + " addresses.")
    print("New file is Written!")
    df.to_csv(filename, index=None, header=True)


def ConvertAddressToCoord(filename, output):
    df = pd.read_csv(filename)
    df.insert(df.shape[1], 'Lat', np.NAN)
    df.insert(df.shape[1], 'Lon', np.NAN)
    buffer_threshold = 1000
    start_index = 0
    data_size = 0
    address_dict = {}
    # add the existed coordinates into dict
    for row in df.iterrows():
        index = row[0]
        address = df.iloc[index].at["BurnAddress"]
        lat_deg = df.iloc[index].at["LatDeg"]
        lat_min = df.iloc[index].at["LatMin"]
        lat_sec = df.iloc[index].at["LatSec"]
        lng_deg = df.iloc[index].at["LonDeg"]
        lng_min = df.iloc[index].at["LonMin"]
        lng_sec = df.iloc[index].at["LonSec"]
        coord_origin = np.array([lat_deg, lat_min, lat_sec, lng_deg, lng_min, lng_sec])
        contain_nan = (True in np.isnan(coord_origin))
        if not contain_nan:
            lat = convertCoordToFloat(lat_deg, lat_min, lat_sec)
            long = convertCoordToFloat(lng_deg, lng_min, lng_sec)
            if long > 0:
                long = -1 * long
            address_dict[address] = (lat, long)
    # covert all address to coordinate
    for row in df.iterrows():
        index = row[0]
        address = df.iloc[index].at["BurnAddress"]
        if address in address_dict.keys():
            lat, long = address_dict[address]
        else:
            # lat, long = fakeConvertAddress(address)
            lat, long = convertAddress(address)
            address_dict[address] = (lat, long)
        df.loc[index, "Lat"] = lat
        df.loc[index, "Lon"] = long
        if np.isnan(lat) or np.isnan(long):
            print("Invalid Address, id = " + str(df.iloc[index].at["id"]))
        # Buffer Writing
        data_size += 1
        if data_size >= buffer_threshold:
            if start_index == 0:
                buffer_df = df[start_index: start_index + data_size]
                buffer_df.to_csv(output, index=None, header=True)
                start_index = start_index + data_size
                data_size = 0
            else:
                buffer_df = df[start_index: start_index + data_size]
                buffer_df.to_csv(output, mode='a', index=None, header=False)
                start_index = start_index + data_size
                data_size = 0
    buffer_df = df[start_index: start_index + data_size]
    buffer_df.to_csv(output, mode='a', index=None, header=False)


def convertAddress(address):
    state = "+Georgia, Uinted States"
    API_KEY = "use-your-own-key"
    url = "https://maps.googleapis.com/maps/api/geocode/json?address=" + address + state + "&key=" + API_KEY
    res = requests.get(url)
    print(url)
    json_str = res.text
    obj = json.loads(json_str)
    status = obj["status"]
    if status == "OK":
        coord = obj["results"][0]["geometry"]["location"]
        return coord['lat'], coord['lng']
    else:
        return np.NAN, np.NAN


def convertCoordToFloat(deg, minutes, sec):
    return deg + minutes / 60 + sec / 3600


def fakeConvertAddress(address):
    return np.NAN, np.NAN


def ConvertAddressByDict(filename, output):
    df = pd.read_csv(filename)
    # Find valid data, store the lat, long for the address to the dict
    valid_dict = {}
    lat = df["Lat"]
    long = df["Lon"]
    addr = df["BurnAddress"]
    # This is a function for GA records
    # Get GA boundary
    sf = shp.Reader("./Data/State_Boundary/cb_2018_us_state_500k.shp")
    poly_coord = []
    for shape in sf.shapeRecords():
        if shape.record[4] == "GA":
            for i in shape.shape.points[:]:
                coord = (i[0], i[1])
                poly_coord.append(coord)
    polygon = Polygon(poly_coord)
    invalid_number = 0
    for i in range(0, len(lat)):
        lat_tmp = lat[i]
        long_tmp = long[i]
        addr_tmp = addr[i]
        fire_point = Point(long_tmp, lat_tmp)
        valid_addr = polygon.contains(fire_point)
        if valid_addr:
            if addr_tmp in valid_dict.keys():
                continue
            else:
                valid_dict[addr_tmp] = (long_tmp, lat_tmp)
    # Write the valid address to the new data frame
    df_new = df.copy()
    df_new.loc[:, "Lat"] = np.NaN
    df_new.loc[:, "Lon"] = np.NaN
    for row in df_new.iterrows():
        index = row[0]
        addr_new = df_new.iloc[index].at["BurnAddress"]
        if addr_new in valid_dict.keys():
            long_new, lat_new = valid_dict[addr_new]
            df_new.loc[index, "Lat"] = lat_new
            df_new.loc[index, "Lon"] = long_new
        else:
            invalid_number += 1
            print("Invalid Address: " + str(df_new.iloc[index].at["id"]))

    print("New file is Written!")
    print("There are " + str(invalid_number) + " invalid data.")
    df_new.to_csv(output, index=None, header=True)


def DeleteInvalidAddress(filename):
    df = pd.read_csv(filename)
    address = df['BurnAddress'].astype(str)
    delete_idx = []
    for i in range(0, len(address)):
        address_tmp = str(address[i])
        if address_tmp == "nan":
            delete_idx.append(i)
    df = df.drop(df.index[delete_idx])
    print("Delete " + str(len(delete_idx)) + " invalid address.")
    df.to_csv(filename, index=None, header=True)


def SplitCSV(filename, datasize, outputpath):
    df = pd.read_csv(filename)
    start_idx = 0
    split_num = 0
    while start_idx < len(df):
        df_split = df[start_idx: start_idx + datasize]
        output_name = outputpath + "split_" + str(split_num) + ".csv"
        df_split.to_csv(output_name, index=False)
        split_num = split_num + 1
        start_idx = start_idx + datasize


def convertAddressImproved(address):
    # The bounds parameter defines the latitude/longitude coordinates
    # of the southwest and northeast corners of this bounding box
    API_KEY = "use-your-own-key"
    params = {
        'key': API_KEY,
        'address': address,
        'region': 'us',
        'bounds': '30.360,-85.606|35.001,-80.843'
    }
    baseurl = "https://maps.googleapis.com/maps/api/geocode/json?"
    res = requests.get(baseurl, params=params).json()
    status = res["status"]
    if status == "OK":
        coord = res["results"][0]["geometry"]["location"]
        return coord['lat'], coord['lng']
    else:
        return np.NAN, np.NAN



def convertAddressBing(address):
    # The bounds parameter defines the latitude/longitude coordinates
    # of the southwest and northeast corners of this bounding box
    API_KEY = "use-your-own-key"
    params = {
        'addressLine': address,
        'key': API_KEY,
        'countryRegion': 'US',
        'strictMatch': 1,
        'adminDistrict': 'GA'
    }
    baseurl = "http://dev.virtualearth.net/REST/v1/Locations?"
    res = requests.get(baseurl, params=params).json()
    if "errorDetails" in res.keys():
        print(res["errorDetails"])
        return np.NAN, np.NAN, np.NAN
    elif res['resourceSets'][0]['estimatedTotal'] == 0:
        return np.NAN, np.NAN, np.NAN
    else:
        lat, long = res['resourceSets'][0]['resources'][0]['point']['coordinates']
        found_address = res['resourceSets'][0]['resources'][0]["name"]
        print(lat, long, found_address)
        return lat, long, found_address


def convertAddressGoogle(address):
    # The bounds parameter defines the latitude/longitude coordinates
    # of the southwest and northeast corners of this bounding box
    API_KEY = "use-your-own-key"
    params = {
        'key': API_KEY,
        'address': address,
        'region': 'us',
        'bounds': '30.360,-85.606|35.001,-80.843'
    }
    baseurl = "https://maps.googleapis.com/maps/api/geocode/json?"
    res = requests.get(baseurl, params=params).json()
    status = res["status"]
    if status == "OK":
        coord = res["results"][0]["geometry"]["location"]
        address_name = res["results"][0]["formatted_address"]
        # print(coord['lat'], coord['lng'], address_name)
        return coord['lat'], coord['lng'], address_name
    else:
        return np.NAN, np.NAN, np.NAN

