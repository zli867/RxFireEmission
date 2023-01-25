from datetime import datetime
import pandas as pd
import os


def ConvertToCsv(filename, output_name, year):
    df = pd.read_csv(filename, dtype={'DAY': int, 'POLYID': str, 'FIREID': str, 'GENVEG': int,
                                      'LATI': float, 'LONGI': float, 'AREA': float, 'BMASS': float,
                                      'CO2': float, 'CO': float, 'CH4': float, 'NMOC': float, 'H2': float,
                                      'NOXasNO': float, 'SO2': float, 'PM25': float, 'TPM': float, 'TPC': float,
                                      'OC': float, 'BC': float, 'NH3': float, 'NO': float, 'NO2': float, 'NMHC': float,
                                      'PM10': float, 'APIN': float,'BENZENE': float, 'BIGALK': float, 'BIGENE': float,
                                      'BPIN': float, 'BZALD': float, 'C2H2': float, 'C2H4': float, 'C2H6': float, 'C3H6': float,
                                      'C3H8': float, 'CH2O': float, 'CH3CH2OH': float, 'CH3CHO': float,'CH3CN': float,'CH3COCH3': float,
                                      'CH3COOH': float,'CH3OH': float,'CRESOL': float, 'GLYALD': float, 'HCN': float, 'HCOOH': float, 'HONO': float,
                                      'HYAC': float, 'ISOP': float, 'LIMON': float, 'MACR': float, 'MEK': float, 'MGLY': float, 'MVK': float, 'MYRC': float,
                                      'PHENOL': float, 'TOLUENE': float, 'XYLENE': float, 'XYLOL': float})
    date = []
    for idx, row in df.iterrows():
        day_num = str(row['DAY'])
        day_of_data = day_num.rjust(3, '0')
        date_of_data = str(year) + "-" + day_of_data
        date_obj = datetime.strptime(date_of_data, "%Y-%j")
        date_str = datetime.strftime(date_obj, "%Y-%m-%d")
        date.append(date_str)
    df['DAY'] = date
    # Save the data
    df.to_csv(output_name, index=False)



location_path = "/storage/home/hcoda1/7/zli867/p-ar70-0/FINN/Data/"
filenames = []
for filename_tmp in os.listdir(location_path):
    if ".txt" in filename_tmp:
        filenames.append(filename_tmp)
print(filenames)
idx = 0
for filename in filenames:
    filepath = location_path + filename
    outputname = location_path + "2021_" + str(idx) + ".csv"
    print("Converted " + filename)
    ConvertToCsv(filepath, outputname, 2021)
    idx = idx + 1

# combined
# Coaser Filter
lat_max = 50
lat_min = 20
lon_max = -70
lon_min = -120

filenames = []
for filename_tmp in os.listdir(location_path):
    if ".csv" in filename_tmp:
        filenames.append(filename_tmp)

idx = 0
res_df = None
for filename in filenames:
    print(filename)
    df = pd.read_csv(location_path + filename)
    if idx == 0:
        res_df = pd.DataFrame(columns=df.columns)
    df = df[(df['LATI'] >= lat_min) & (df['LATI'] <= lat_max) &
            (df['LONGI'] >= lon_min) & (df['LONGI'] <= lon_max)]
    res_df = pd.concat([res_df, df], ignore_index=True)
    idx = idx + 1
res_df.to_csv("Combined.csv", index=False)