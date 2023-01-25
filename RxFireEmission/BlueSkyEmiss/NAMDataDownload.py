import os
from datetime import datetime, timedelta

start_time = datetime(2021, 1, 1)
end_time = datetime(2021, 12, 31)

current_time = start_time
while current_time <= end_time:
    url = "ftp://ftp.arl.noaa.gov/pub/archives/nam12/"+ current_time.strftime("%Y%m%d") + "_nam12"
    command = "wget " + url
    os.system(command)
    current_time += timedelta(days=1)