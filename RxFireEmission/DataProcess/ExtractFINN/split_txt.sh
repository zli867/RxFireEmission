#!/bin/bash
# This script splits the large FINN original data file into several small files.

FILENAME=FINNv2.5_modvrs_MOZART_2020_c20211213.txt
HDR=$(head -1 $FILENAME)   # Pick up CSV header line to apply to each file
tail -n +2 $FILENAME > tmp.txt
split -l 100000 tmp.txt xyz  # Split the file into chunks of 20 lines each
n=1
for f in xyz*              # Go through all newly created chunks
do
   echo $HDR > emis_2021_${n}.txt    # Write out header to new file called "Part(n)"
   cat $f >> emis_2021_${n}.txt      # Add in the 20 lines from the "split" command
   rm $f                   # Remove temporary file
   ((n++))                 # Increment name of output part
done
rm tmp.txt
