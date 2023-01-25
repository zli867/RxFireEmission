import pandas as pd
from datetime import datetime
import numpy as np

# # Yeas include acres
filenames = ["/Users/zongrunli/Desktop/RxFireEmission/results/permits/FL_2014.csv",
             "/Users/zongrunli/Desktop/RxFireEmission/results/permits/FL_2017.csv",
             "/Users/zongrunli/Desktop/RxFireEmission/results/permits/FL_2018.csv",
             "/Users/zongrunli/Desktop/RxFireEmission/results/permits/FL_2019.csv",
             "/Users/zongrunli/Desktop/RxFireEmission/results/permits/FL_2020.csv",
             "/Users/zongrunli/Desktop/RxFireEmission/results/permits/FL_2021.csv"]
output_files = []
for filename in filenames:
    df = pd.read_csv(filename)
    res_df = pd.DataFrame(columns=('Id', 'State', 'Time', 'Lat', 'Lon', 'Burned_Area', 'Duration'))
    duration = []
    removed_idx = []
    for index, row in df.iterrows():
        starte_date = datetime.strptime(row['START_DATE'], '%Y-%m-%d')
        end_date = datetime.strptime(row['END_DATE'], '%Y-%m-%d')
        if row["PILES"] != 0 or row["PILE_HEIGH"] != 0 or row["PILE_WIDTH"] != 0:
            removed_idx.append(index)
        duration_tmp = end_date - starte_date
        duration.append(duration_tmp.days)
    res_df['Id'] = df['PK']
    res_df['State'] = ['FL'] * len(df)
    res_df['Time'] = df['START_DATE']
    res_df['Lat'] = df['LAT']
    res_df['Lon'] = df['LON']
    res_df['Burned_Area'] = df['ACRES']
    res_df['Duration'] = duration
    res_df = res_df.drop(removed_idx)
    res_df.to_csv(filename[0: -4] + "_extracted.csv", index=False)
    output_files.append(filename[0: -4] + "_extracted.csv")

# Year does not include acres
filenames = ["/Users/zongrunli/Desktop/RxFireEmission/results/permits/FL_2013.csv",
             "/Users/zongrunli/Desktop/RxFireEmission/results/permits/FL_2015.csv",
             "/Users/zongrunli/Desktop/RxFireEmission/results/permits/FL_2016.csv"]
for filename in filenames:
    df = pd.read_csv(filename)
    res_df = pd.DataFrame(columns=('Id', 'State', 'Time', 'Lat', 'Lon', 'Burned_Area', 'Duration'))
    duration = []
    burned_area = []
    for index, row in df.iterrows():
        starte_date = datetime.strptime(row['START_DATE'], '%Y-%m-%d')
        end_date = datetime.strptime(row['END_DATE'], '%Y-%m-%d')
        duration_tmp = end_date - starte_date
        duration.append(duration_tmp.days)
        # Calculate Burned Area
        size_of_bu = row['SIZE_OF_BU']
        if 'acres' in size_of_bu:
            str_list = size_of_bu.split()
            burned_area.append(float(str_list[0]))
        else:
            # burned_area_tmp = row['PILES'] * row['PILE_WIDTH'] * row['PILE_HEIGH']
            burned_area_tmp = np.nan
            burned_area.append(burned_area_tmp)
    res_df['Id'] = df['PK']
    res_df['State'] = ['FL'] * len(df)
    res_df['Time'] = df['START_DATE']
    res_df['Lat'] = df['LAT']
    res_df['Lon'] = df['LON']
    res_df['Burned_Area'] = burned_area
    res_df['Duration'] = duration
    res_df.to_csv(filename[0: -4] + "_extracted.csv", index=False)
    output_files.append(filename[0: -4] + "_extracted.csv")


# Combine csv
idx = 0
res_df = None
for output_file in output_files:
    df = pd.read_csv(output_file)
    if idx == 0:
        res_df = pd.DataFrame(columns=df.columns)
    res_df = pd.concat([res_df, df], ignore_index=True)
    idx = idx + 1
res_df.to_csv("/Users/zongrunli/Desktop/RxFireEmission/results/permits/FL_2013_2021_permits.csv", index=False)
