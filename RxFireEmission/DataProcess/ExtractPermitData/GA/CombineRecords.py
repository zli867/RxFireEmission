import pandas as pd


# Combine all records and delete the overlap records
filenames = ["/Users/zongrunli/Desktop/SEEmission/ExtractPermitData/GA/Data/validRecords/2015_GA.csv",
             "/Users/zongrunli/Desktop/SEEmission/ExtractPermitData/GA/Data/validRecords/2016_GA.csv",
             "/Users/zongrunli/Desktop/SEEmission/ExtractPermitData/GA/Data/validRecords/2017_2018_GA.csv",
             "/Users/zongrunli/Desktop/SEEmission/ExtractPermitData/GA/Data/validRecords/2019_2020_GA.csv",
             "/Users/zongrunli/Desktop/SEEmission/ExtractPermitData/GA/Data/validRecords/2020_GA.csv"]
idx = 0
res_df = None
for filename in filenames:
    if idx == 0:
        res_df = pd.read_csv(filename)
    else:
        df = pd.read_csv(filename)
        res_df = pd.concat([res_df, df], ignore_index=True)
    idx = idx + 1

ori_records = len(res_df)

# Remove duplicate records
res_df = res_df.drop_duplicates(subset=['id'])
new_records = len(res_df)
print("Removed " + str(ori_records - new_records) + " Records")

res_df.to_csv("/Users/zongrunli/Desktop/SEEmission/ExtractPermitData/GA/Data/CombinedGA_2.csv", index=False, header=True)