import pandas as pd
import numpy as np


def is_number(s):
    try:
        float(s)
        return True
    except ValueError:
        pass

    try:
        import unicodedata
        unicodedata.numeric(s)
        return True
    except (TypeError, ValueError):
        pass

    return False


filename = "/Users/zongrunli/Desktop/RxFireEmission/results/permits/SC_2013_2021.csv"
sc_df = pd.read_csv(filename, dtype={"Id": str, "State": str, "Burned_Area": str, "Burn_Type": str})


sc_df["Burned_Area"] = sc_df["Burned_Area"].fillna("missing")
invalid_idx = []
for idx, row in sc_df.iterrows():
    if is_number(row["Burned_Area"]):
        continue
    else:
        invalid_idx.append(idx)

sc_df = sc_df.drop(invalid_idx)
sc_df = sc_df[sc_df["Burn_Type"] != "PILED DEBRIS"]
sc_df = sc_df[sc_df["Lat"] > 0]
sc_df.to_csv("/Users/zongrunli/Desktop/RxFireEmission/results/permits/Cleaned_SC_2013_2021_permits.csv", index=False)
