import geopandas


def convertToCSV(filename, output_name):
    data = geopandas.read_file(filename)
    # Transfer the geometry to WGS84
    data = data.to_crs(epsg=4326)
    lat = []
    lon = []
    for index, row in data.iterrows():
        fire_point = row['geometry']
        fire_lon = fire_point.x
        fire_lat = fire_point.y
        lat.append(fire_lat)
        lon.append(fire_lon)
    original_features = data.columns
    select_features = []
    for i in range(0, len(original_features)):
        if original_features[i] == 'geometry':
            continue
        else:
            select_features.append(original_features[i])
    res_df = data[select_features]
    res_df['LAT'] = lat
    res_df['LON'] = lon
    res_df.to_csv(output_name, index=False)


for year in range(2013, 2022):
    print("Extracting " + str(year))
    output_name = "/Users/zongrunli/Desktop/RxFireEmission/results/permits/FL_" + str(year) + ".csv"
    filename = "/Users/zongrunli/Desktop/RxFireEmission/data/permit_data/FL/OBA_" + str(year) + ".shp"
    convertToCSV(filename, output_name)
