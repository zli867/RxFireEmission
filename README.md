# RxFireEmission
## Environment Set Up
The environment is validated in a MacOS laptop. Use the following command to build up the python environment.
```
conda env create -f datafusion.yml
```

## Code Description
This project mainly include four modules:
* BlueSkyEmiss: This module provide scripts for:
    * Generating BlueSky input from provided permit data or FINN data;
    * Running BlueSky output by using certain configuration, metereology input and burning records;
    * Generating Gird-based CMAQ 3D fire emission data from BlueSky output.

* BurnTypeDifferentiation: This module provide scripts for:
    * Agricultural fires seperation from FINN data or permit data;
    * Wildfire detection algorithm and elbow method for hyper-parameter selection;
    * A burn type differentiation driver for FINN and permit data. This is an example for using the algorithms implemented in this module. FINN records will be differentiated into wildfires, prescribed burning and agricultural burning. Permit will be differentiated into prescribed burning and agricultural burning.

* DataProcess: This module provide scripts for:
    * Extract FINN data by state boundaries, combined fires by fire ID and convert the data format to csv.
    * Extract permit data for South Carolina, Georgia and Florida. For Georgia data, we both provide Google geocoding and Bing geocoding examples. In the manuscript, we conduct the Google geocoding. Thanks for all these APIs.
    * Extract wildfire records from NIFC history records.

* FireMatching: This module provide scripts for:
    * Fire-to-fire matching algorithms: nearest distance matching and relaxation matching.
    * Grid-based matching.
    * Statewide matching.

* util: Some helper functions conducted in several modules.

## Data
Due to the size of data, we store our data at:. Or directly contact author for requirements. The data directory does not include all the data for runing the modules. You should at least download county, federal land and U.S. state shapefile data and put them in data directory. Also, the grid definition data is based on CMAQ GRIDCRO2D.nc. You should also consider generate your own grid definition and put it in the directory.

## Permit Tabular Structure
*  Data features
    | State | Time (start time) |latitude|longitude|burned_area (acres)|others|landcover (after agr sep alg)
    | ------ | ----| ------ | ----| ------ |---|---|

## FINN Tabular Structure
*  Data features
    | DAY | FIREID (unique) |AREA (acres)|LATI|LONGI|landcover (after agr sep alg)|
    | ------ | ----| ------ | ----| ------ |---|

## Authorship
* The paper for the modules is submitted to Remote Sensing.

* The code is implemented by Zongrun Li (zli867@gatech.edu)
