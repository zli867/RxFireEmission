from datetime import datetime
import pandas as pd
from AgriculturalSeperation import seperate_ag_fires
from WildfireSeperation import seperate_wildfires


def burn_type_differentiation(filename):
    dateparse = lambda x: datetime.strptime(x, '%Y-%m-%d')
    df = pd.read_csv(filename, parse_dates=['DAY'], date_parser=dateparse)

    # STEP 1: Add LAND_COVER feature to FINN, extract agricultural fire
    agr_output_name = filename[:-4] + "_agr.csv"
    invalid_output_name = filename[:-4] + "_invalid.csv"
    valid_output_name = filename[:-4] + "_rx_wf.csv"
    agri_df, invalid_df, valid_df = seperate_ag_fires(filename)

    # print statistics
    print(filename)
    print("Total records: " + str(len(df)))
    print("Agricultural records: " + str(len(agri_df)))
    print("Invalid records: " + str(len(invalid_df)))

    # save data
    agri_df.to_csv(agr_output_name, index=False)
    invalid_df.to_csv(invalid_output_name, index=False)

    # SEPERATE WILDFIRE RX FROM VALID_DF
    valid_df_copy = valid_df.copy()
    wildfire_res = seperate_wildfires(valid_df_copy)
    wildfire_output_name = filename[:-4] + "_wf.csv"
    wildfire_res.to_csv(wildfire_output_name, index=False)
    wildfire_id = set(list(wildfire_res["FIREID"].to_numpy()))

    # SEPERATE RX
    rx_index = []
    for index, row in valid_df.iterrows():
        if row["FIREID"] in wildfire_id:
            continue
        else:
            rx_index.append(index)
    rx = valid_df_copy.loc[rx_index, :]
    rx = rx.reset_index(drop=True)
    output_name = filename[:-4] + "_rx.csv"
    rx.to_csv(output_name, index=False)

    print("Wildfire records: " + str(len(wildfire_res)))
    print("Rx records: " + str(len(rx)))