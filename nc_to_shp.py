import os
import numpy as np
import csv
import time
from netCDF4 import Dataset

firstRead = 1
relativepath = "X:\\Hamilton\\SpatialLabBaseData\\NZ\\Climate\\CCII"

t0 = time.clock()
for subdir, dirs, files in os.walk(relativepath):
  for file in files:
    filepath = os.path.join(subdir, file)
		
    if filepath.endswith(".nc"):
      if firstRead:
        fileEnding = "table.csv"
        firstRead = 0
      else:
        fileEnding = "output.csv"
      print (filepath) +"\n", os.path.realpath("") + os.sep + fileEnding + "\n", os.path.realpath("") + os.sep + "output.csv"
      rootgrp = Dataset(filepath, "r", format="NETCDF4")
      lats = rootgrp["latitude"][:]
      longs = rootgrp["longitude"][:]
      timeData = rootgrp["time"][:]
      varTitle = ""
      datapoint = rootgrp["time"][:]

      for var in iter(rootgrp.variables):
			
        if var != "longitude" and var != "latitude" and var != "elevation" and var != "time_bnds":
					datapoint = rootgrp[var]
					varTitle = var
      
      with open(os.path.realpath("") + os.sep + fileEnding, "rb") as inputfile:
        with open(os.path.realpath("") + os.sep + "temp.csv", "wb") as outputfile:
          reader = csv.reader(inputfile)
          writer = csv.writer(outputfile)
          row = reader.next()
          row.append(varTitle)
          writer.writerow(row)
        
          for row in reader:
       
            # latitude index
            lati = np.argmin(np.abs(lats - np.float32(row[2])))
            # longitude index
            longi = np.argmin(np.abs(longs - np.float32(row[3])))
            row.append(datapoint[1][lati][longi])
            writer.writerow(row)

      os.remove(os.path.realpath("") + os.sep + "output.csv")
      os.rename(os.path.realpath("") + os.sep + "temp.csv", os.path.realpath("") + os.sep + "output.csv")
      rootgrp.close()
print time.clock()-t0
