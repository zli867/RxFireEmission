from datetime import datetime
import pandas as pd
from BurnTypeDifferentiation import burn_type_differentiation
from DataProcess.ExtractFINN import ExtractByBoundary


# I include part of FINN data cleaning in this driver. Although you can always use the DataProcess Module
start_year = 2021
end_year = 2021

southeastern_states = ["Alabama", "Georgia", "Tennessee", "Florida", "Mississippi",
                       "North Carolina", "South Carolina", "Arkansas", "Louisiana",
                       "Kentucky", "Virginia", "West Virginia"]

state_abbr = {"Alabama": "AL", "Georgia": "GA", "Tennessee": "TN", "Florida": "FL", "Mississippi": "MS",
              "North Carolina": "NC", "South Carolina": "SC", "Arkansas": "AR", "Louisiana": "LA",
              "Kentucky": "KY", "Virginia": "VA", "West Virginia": "WV"}

sum_variable_name = ["AREA", "BMASS", "CO2", "CO", "CH4", "NMOC", "H2", "NOXasNO", "SO2", "PM25",
                     "TPM", "TPC", "OC", "BC", "NH3", "NO", "NO2", "NMHC", "PM10", " APIN", "BENZENE", "BIGALK",
                     "BIGENE",
                     "BPIN", "BZALD", "C2H2", "C2H4", "C2H6", "C3H6", "C3H8", "CH2O", "CH3CH2OH", "CH3CHO", "CH3CN",
                     "CH3COCH3",
                     "CH3COOH", "CH3OH", "CRESOL", "GLYALD", "HCN", "HCOOH", "HONO", "HYAC", "ISOP", "LIMON", "MACR",
                     "MEK", "MGLY",
                     "MVK", "MYRC", "PHENOL", "TOLUENE", "XYLENE", "XYLOL"]

# Data Processing
work_dir = "/Users/zongrunli/Desktop/emiss_work_dir/"
for year in range(start_year, end_year + 1):
    input_name = work_dir + "res_emiss_" + str(year) + ".csv"
    for state_name in southeastern_states:
        output_state_name = work_dir + state_name + str(year) + "_MODIS_VIIRS.csv"
        ExtractByBoundary.extractByState(input_name, output_state_name, state_name)
        print("Finish " + state_name)

col_order = None
for southeastern_state in southeastern_states:
    filenames = []
    for year in range(start_year, end_year + 1):
        filename = work_dir + southeastern_state + str(year) + "_MODIS_VIIRS.csv"
        filenames.append(filename)

    finn_data = []

    for filename in filenames:
        df = pd.read_csv(filename)
        col_order = df.columns
        # sum the fire by fire id,
        area_emiss = df.groupby(['FIREID'])[sum_variable_name].sum()
        # convert m2 to acres
        area_emiss["AREA"] = area_emiss["AREA"] * 0.000247105
        df = df.drop_duplicates(subset=['FIREID'])
        # Helper DF
        columns_name = ["FIREID"]
        columns_name.extend(sum_variable_name)
        df_tmp = pd.DataFrame(columns=columns_name)
        df_tmp["FIREID"] = area_emiss.index
        df_tmp[sum_variable_name] = area_emiss.values
        # Same data type for key
        df_tmp["FIREID"] = df_tmp["FIREID"].astype(int)
        df["FIREID"] = df["FIREID"].astype(int)
        # delete area in original dataframe, use new summed area to replace.
        select_features = list(df.columns)
        for feature in sum_variable_name:
            select_features.remove(feature)
        # LEFT JOIN
        df = df[select_features]
        df = pd.merge(df_tmp, df, how="left", on=["FIREID"])
        # RESET IDX
        df = df.reset_index(drop=True)
        finn_data.append(df)

    res = pd.concat(finn_data)
    res = res[res["AREA"] > 0]
    # Generate new fire id
    state_name = state_abbr[southeastern_state] + "_FINN_MODIS_VIIRS"
    fire_id = []
    for i in range(0, len(res)):
        fire_id_tmp = state_name + str(i).rjust(len(str(len(res))), '0')
        fire_id.append(fire_id_tmp)

    res["FIREID"] = fire_id
    # reorder
    res = res[col_order]
    output_file_name = state_abbr[southeastern_state] +"_Combined_MODIS_VIIRS.csv"
    res.to_csv(work_dir + output_file_name, index=False)

# Combine file to one file (SE_Combined_MODIS_VIIRS)
df_array = []
for southeastern_state in southeastern_states:
    current_filename = work_dir + state_abbr[southeastern_state] +"_Combined_MODIS_VIIRS.csv"
    df = pd.read_csv(current_filename)
    df_array.append(df)
df_res = pd.concat(df_array)
df_res.to_csv(work_dir + "SE_Combined_MODIS_VIIRS.csv", index=False)

#############################
# Burn Type differentiation #
#############################
# finn_filename = "SE_Combined_MODIS_VIIRS.csv"
# dateparse = lambda x: datetime.strptime(x, '%Y-%m-%d')
# finn_df = pd.read_csv(work_dir + finn_filename, parse_dates=['DAY'], date_parser=dateparse)
#
# # STEP 1: Add LAND_COVER feature to FINN, extract agricultural fire
# agr_output_name = finn_filename[:-4] + "_agr.csv"
# invalid_output_name = finn_filename[:-4] + "_invalid.csv"
# valid_output_name = finn_filename[:-4] + "_rx_wf.csv"
# agri_df, invalid_df, valid_df = seperate_ag_fires(work_dir + finn_filename)
#
# # print statistics
# print(finn_filename)
# print("Total records: " + str(len(finn_df)))
# print("Agricultural records: " + str(len(agri_df)))
# print("Invalid records: " + str(len(invalid_df)))
#
# # save data
# agri_df.to_csv(work_dir + agr_output_name, index=False)
# invalid_df.to_csv(work_dir + invalid_output_name, index=False)
#
# # SEPERATE WILDFIRE RX FROM VALID_DF
# valid_df_copy = valid_df.copy()
# wildfire_res = seperate_wildfires(valid_df_copy)
# wildfire_output_name = finn_filename[:-4] + "_wf.csv"
# wildfire_res.to_csv(work_dir + wildfire_output_name, index=False)
# wildfire_id = set(list(wildfire_res["FIREID"].to_numpy()))
#
# # SEPERATE RX
# rx_index = []
# for index, row in valid_df.iterrows():
#     if row["FIREID"] in wildfire_id:
#         continue
#     else:
#         rx_index.append(index)
# rx = valid_df_copy.loc[rx_index, :]
# rx = rx.reset_index(drop=True)
# output_name = finn_filename[:-4] + "_rx.csv"
# rx.to_csv(work_dir + output_name, index=False)
#
# print("Wildfire records: " + str(len(wildfire_res)))
# print("Rx records: " + str(len(rx)))

finn_filename = work_dir + "SE_Combined_MODIS_VIIRS.csv"
burn_type_differentiation(finn_filename)