import pandas as pd
from datetime import datetime

# The data in South Carolina has columns:
# 'BURN_NUMBER', 'CFS NUMBER', 'BURN_TYPE', 'RECEIVED', 'TIME_STRT',
#        'CATEGORY DAY', 'COUNTY', 'CPFM?', 'ACRES', 'TOTAL_TONS', 'LONGLEAF?',
#        'LATITUDE', 'LONGITUDE', 'FISCAL YEAR', 'MONTH', 'WEEKDAY',
#        'START HOUR'
# Burned area unit is acres, total mass unit is tons
filenames = ["/Users/zongrunli/Desktop/RxFireEmission/data/permit_data/SC/Burn NotificationsCY_2013-2017.xlsx",
             "/Users/zongrunli/Desktop/RxFireEmission/data/permit_data/SC/Burn Notifications CY_2018-2021.xlsx"]
output_filename = "/Users/zongrunli/Desktop/RxFireEmission/results/permits/SC_2013_2021.csv"

features = ['BURN_NUMBER', 'CFS NUMBER', 'BURN_TYPE', 'RECEIVED', 'TIME_STRT',
            'CATEGORY DAY', 'COUNTY', 'CPFM?', 'ACRES', 'TOTAL_TONS', 'LONGLEAF?',
            'LATITUDE', 'LONGITUDE', 'FISCAL YEAR', 'MONTH', 'WEEKDAY',
            'START HOUR']
select_features = ('Id', 'State', 'Time', 'Lat', 'Lon', 'Burned_Area', 'Burn_Type', 'Total_Mass', 'Start_Hour','County')
# output_df = pd.DataFrame(columns=select_features)
res_list = []
for idx in range(0, len(filenames)):
    filename = filenames[idx]
    burn_df = pd.read_excel(filename)
    # Fill the features
    res_df = pd.DataFrame(columns=select_features)
    res_df['State'] = ['SC'] * len(burn_df)
    res_df['Lat'] = burn_df['LATITUDE']
    res_df['Lon'] = burn_df['LONGITUDE']
    res_df['Burned_Area'] = burn_df['ACRES']
    res_df['Burn_Type'] = burn_df['BURN_TYPE']
    res_df['Total_Mass'] = burn_df['TOTAL_TONS']
    res_df['County'] = burn_df['COUNTY']
    res_df['Id'] = burn_df['BURN_NUMBER']

    output_time_format = "%Y-%m-%d"
    time_res = []
    hour_res = []
    for i in range(0, len(burn_df)):
        time_original = burn_df.iloc[i]['RECEIVED']
        hour_original = burn_df.iloc[i]['TIME_STRT']
        datetime_str = datetime.strftime(time_original, "%Y-%m-%d")
        hour_str = datetime.strftime(hour_original, "%H:%M:%S")
        # date_str = datetime_str + " " + hour_str
        time_res.append(datetime_str)
        hour_res.append(hour_str)
    res_df['Time'] = time_res
    res_df['Start_Hour'] = hour_res
    res_list.append(res_df)

output_df = pd.concat(res_list)
output_df["Id"] = output_df["Id"].fillna("missing")
output_df = output_df.reset_index(drop=True)
# Fill the missing ID
state_name = "SC"
id_idx = 0
for idx, row in output_df.iterrows():
    if row["Id"] == "missing":
        new_id = state_name + str(id_idx).rjust(7, '0')
        output_df.at[idx, 'Id'] = new_id
        id_idx += 1
output_df.to_csv(output_filename, index=False)

