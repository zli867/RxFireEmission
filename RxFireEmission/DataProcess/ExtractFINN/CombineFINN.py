import pandas as pd
import ExtractByBoundary

southeastern_states = ["Alabama", "Georgia", "Tennessee", "Florida", "Mississippi",
                       "North Carolina", "South Carolina", "Arkansas", "Louisiana",
                       "Kentucky", "Virginia", "West Virginia"]

state_abbr = {"Alabama": "AL", "Georgia": "GA", "Tennessee": "TN", "Florida": "FL", "Mississippi": "MS",
                       "North Carolina": "NC", "South Carolina": "SC", "Arkansas": "AR", "Louisiana": "LA",
                       "Kentucky": "KY", "Virginia": "VA", "West Virginia": "WV"}

input_name = "/Volumes/Zongrun's Backup Drive/2022/Southeastern Emission/FINN MODIS/res_emiss_2020.csv"
output_path = "/Volumes/Zongrun's Backup Drive/2022/Southeastern Emission/FINN MODIS/Result/"

# Extract FINN By Boundary
for state_name in southeastern_states:
    for year in range(2013, 2021):
        output_state_name = output_path + state_name + str(year) + "_MODIS_VIIRS.csv"
        ExtractByBoundary.extractByState(input_name, output_state_name, state_name)
        print("Finish " + state_name)


sum_variable_name = ["AREA","BMASS","CO2","CO","CH4","NMOC","H2","NOXasNO","SO2","PM25",
                     "TPM","TPC","OC","BC","NH3","NO","NO2","NMHC","PM10"," APIN","BENZENE","BIGALK","BIGENE",
                     "BPIN","BZALD","C2H2","C2H4","C2H6","C3H6","C3H8","CH2O","CH3CH2OH","CH3CHO","CH3CN","CH3COCH3",
                     "CH3COOH","CH3OH","CRESOL","GLYALD","HCN","HCOOH","HONO","HYAC","ISOP","LIMON","MACR","MEK","MGLY",
                     "MVK","MYRC","PHENOL","TOLUENE","XYLENE","XYLOL"]

# Convert Unit, Combined fire, Generate Fire ID
col_order = None
for southeastern_state in southeastern_states:
    filenames = []
    for year in range(2013, 2021):
        filename = output_path + southeastern_state + str(year) + "_MODIS_VIIRS.csv"
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
    res.to_csv(output_file_name, index=False)