import os
import numpy as np
import csv
import time
from netCDF4 import Dataset

#Error class for use when two values are have coordinates that are
#too close to distinguish as different points
class LatLongError(Exception):
  def __init__(self, value):
    self.value = value
  def __str__(self):
    return repr(self.value)

#Boolean for determinig whether to read from table.csv or output.csv
firstRead = True
relativepath = "X:\\Hamilton\\SpatialLabBaseData\\NZ\\Climate\\CCII\\RCP2.6"
#relativepath = "C:\\Github\\nc_to_shp\\data\\RCP2.6"

#Traverse through all files in all subdirectories in the path specified above
for subdir, dirs, files in os.walk(relativepath):
  for filename in files
    #Capture file name for use as variable name prefix in output.csv
    varprefix = filename[:-3]
    filepath = os.path.join(subdir, filename)

    #Only open netCDF4 files
    if filepath.endswith(".nc"):
      if firstRead:
        fileEnding = "table.csv"
        firstRead = False
      else:
        fileEnding = "output.csv"
      #print (filepath) +"\n", os.path.realpath("") + os.sep + fileEnding + "\n", os.path.realpath("") + os.sep + "output.csv"

      #Variable for determining time taken for each file to be read
      t0 = time.clock()
      #Open netCDF4 file and store variables
      rootgrp = Dataset(filepath, "r", format="NETCDF4", diskless=True)
      lats = rootgrp["latitude"][:]
      longs = rootgrp["longitude"][:]
      timeData = rootgrp["time"][:]
      #Vraible title to follw varprefix in output.csv
      varTitle = ""
      #Initialise array to contian the variable of interest from the netCDF4 file
      datapoint = rootgrp["time"][:]

      #Since the variable name contained in the netCDF4 is not known apriori, find it by excluding all known variables
      for var in iter(rootgrp.variables):		
        if var != "longitude" and var != "latitude" and var != "elevation" and var != "time_bnds" and var != "time":
	  datapoint = rootgrp[var]
	  varTitle = var
        
      print "File time: ", time.clock() - t0
      #Variable for determining time taken for full computation to take place
      t0 = time.clock()
      #Open csvs to read from and write to
      with open(os.path.realpath("") + os.sep + fileEnding, "rb") as inputfile:
        with open(os.path.realpath("") + os.sep + "temp.csv", "wb") as outputfile:
          writer = csv.writer(outputfile)
          #Extract elements from csv text to an array
          row = inputfile.next().split(",")
          #Final element is terminated with a carriage return character and new line character, so remove these two characters (\r\n)
          row[len(row)-1] = row[len(row)-1][:-2]
          #Place variable name as first element in new column
          row.append(varprefix + "_" + varTitle)
          writer.writerow(row)
          try:
            for row in inputfile:
              #Extract elements from csv text to an array
              row = row.split(",")
              #Final element is terminated with a carriage return character and new line character, so remove these two characters (\r\n)
              row[len(row)-1] = row[len(row)-1][:-2]
              # latitude index
              lati = np.argwhere(np.abs(lats - np.float32(row[2]))< 0.01)
              # longitude index
              longi = np.argwhere(np.abs(longs - np.float32(row[3]))< 0.01)
              #If no value with coordinates close enough is found, write a missing element to csv
              if len(lati) == 0 or len(longi) == 0: 
                row.append(np.ma.masked)
              #If more than one value with coordinates close enough is found, print terminated in csv and skip to next file
              elif len(lati) > 1 or len(longi) > 1:
                row.append("Terminated")
                writer.writerow(row)
                raise LatLongError("Existence of two values with either latitude or longitude values within 0.01 degrees")
              else:
                row.append(datapoint[:,lati[0],longi[0]].mean())
              writer.writerow(row)
          except LatLongError as e:
              print e.value, "Skipping rest of file. Occured at ", filepath

      #Replace old output.csv with new csv (named temp but renamed to output)    
      os.remove(os.path.realpath("") + os.sep + "output.csv")
      os.rename(os.path.realpath("") + os.sep + "temp.csv", os.path.realpath("") + os.sep + "output.csv")
      #Release the netCDF4 file object
      rootgrp.close()
      print "Computation time: ", time.clock() - t0    
    

