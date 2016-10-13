import os
import sys
import numpy as np
import csv
import time
from netCDF4 import Dataset, num2date

#Error class for use when two values are have coordinates that are
#too close to distinguish as different points
class LatLongError(Exception):
  def __init__(self, value):
    self.value = value
  def __str__(self):
    return repr(self.value)

# Print iterations progress
def printProgress (iteration, total, prefix = '', suffix = '', timetaken = 0, timerecent=0, timesuffix = "seconds"):
    formatStr = "{0:." + str(1) + "f}"
    percents = formatStr.format(100 * (iteration / float(total)))
    sys.stdout.write('\r%s %s%s %s %s %s %s %s %s' % (prefix, percents, '%', suffix, round(timetaken,2), timesuffix, "Last file:", round(timerecent,1), timesuffix)),
    if iteration == total:
        sys.stdout.write('\n')
    sys.stdout.flush()

def getSize(start_path):
    total_size = 0
    for dirpath, dirnames, filenames in os.walk(start_path):
        for f in filenames:
            fp = os.path.join(dirpath, f)
            total_size += os.path.getsize(fp)
    return total_size

inputfileloc = raw_input("Enter the location of input file: ")
outputfileloc = raw_input("Enter the location of output file: ")
inputfileloc = "C:\\Github\\table.csv"
outputfileloc= "C:\\Github\\output.csv"
outputnum = raw_input("Please enter number: ")
outputfileloc= "C:\\Github\\output" + outputnum + ".csv"
if not os.path.isfile(inputfileloc):
  raw_input("Input file does not exist")
  sys.exit()
elif not os.path.isfile(outputfileloc):
  raw_input("Output file does not exist")
  sys.exit()

folder = raw_input("Please enter folder: ")



timeslice = int(raw_input("Please enter a time slice in years: "))

#Boolean for determinig whether to read from table.csv or output.csv
firstRead = True
relativepath = "X:\\Hamilton\\SpatialLabBaseData\\NZ\\Climate\\CCII\\RCP2.6" + folder
totalsize = getSize(relativepath)
print totalsize/(1024*1024*1024), "GB"
currentsize = 0
printProgress(currentsize, totalsize, "Completed so far:",)
t0 = time.clock()
#relativepath = "C:\\Github\\nc_to_shp\\data\\RCP2.6"

#Traverse through all files in all subdirectories in the path specified above
for subdir, dirs, files in os.walk(relativepath):
  for filename in files:
    t1 = time.clock()
    #Capture file name for use as variable name prefix in output.csv
    varprefix = filename[:-3]
    filepath = os.path.join(subdir, filename)
    currentsize += os.path.getsize(filepath)
    #Only open netCDF4 files
    if filepath.endswith(".nc"):
      if firstRead:
        fileloc = inputfileloc
        firstRead = False
      else:
        fileloc = outputfileloc
      #print (filepath) +"\n", os.path.realpath("") + os.sep + fileEnding + "\n", os.path.realpath("") + os.sep + "output.csv"
  
      #Open netCDF4 file and store variables
      t2 = time.clock()
      rootgrp = Dataset(filepath, "r", format="NETCDF4", diskless=True)
      lats = rootgrp["latitude"][:]
      longs = rootgrp["longitude"][:]
      timeData = rootgrp["time"][:]
      timeDiff = 0
      timeDiffSpec = timeData[1]-timeData[0]
      if timeDiff <=370 and timeDiff>=360:
        timeDiff =1
      elif timeDiffSpec <=35 and timeDiffSpec >=25:
        timeDiff =2
      timeData = [num2date(x,rootgrp["time"].units) for x in timeData]
      years = np.asarray([getattr(x, "year") for x in timeData])
      #Vraible title to follw varprefix in output.csv
      varTitle = ""
      #Initialise array to contian the variable of interest from the netCDF4 file
      datapoint = rootgrp["time"][:]
      #Since the variable name contained in the netCDF4 is not known apriori, find it by excluding all known variables
      for var in iter(rootgrp.variables):		
        if var != "longitude" and var != "latitude" and var != "elevation" and var != "time_bnds" and var != "time":
	  datapoint = rootgrp[var]
	  varTitle = var

      #Open csvs to read from and write to
      with open(fileloc, "rb") as inputfile:
        with open(os.path.dirname(outputfileloc) + os.sep + "temp" + outputnum+ ".csv", "wb") as outputfile:
          writer = csv.writer(outputfile)
          #Extract elements from csv text to an array
          row = inputfile.next().split(",")
          #Final element is terminated with a carriage return character and new line character, so remove these two characters (\r\n)
          row[len(row)-1] = row[len(row)-1][:-2]
          #Place variable name as first element in new column
          row.append(varprefix + "_" + varTitle)
          numberOfYears =  len(set(years))/(timeslice)+(len(set(years))%timeslice != 0)
          if len(set(years)) > timeslice:
            row = row + [`(years[0]+(timeslice)*(x-1))` + "-" + `(years[0]+(timeslice)*x-1)` for x in range(2,numberOfYears)] + [`(years[0]+(timeslice)*(numberOfYears-1))` + "-" + `years[years.size-1]` for x in range(0, len(set(years))%(timeslice) != 0)]
          writer.writerow(row)
          try:
            for row in inputfile:
              row = row.split(",")
              #Final element is terminated with a carriage return character and new line character, so remove these two characters (\r\n)
              row[len(row)-1] = row[len(row)-1][:-2]
              # latitude index
              lati = np.argwhere(np.abs(lats - np.float32(row[2]))< 0.01)
              # longitude index
              longi = np.argwhere(np.abs(longs - np.float32(row[3]))< 0.01)
              timei = 0
              for i in range(0,numberOfYears):
                #Extract elements from csv text to an array
                timeio = timei
                year = years[timeio]
                try:
                  timei = np.argwhere(years == years[timeio]+timeslice)[0][0]
                except IndexError:
                  timei=years.size

                #If no value with coordinates close enough is found, write a missing element to csv
                if len(lati) == 0 or len(longi) == 0: 
                  row.append(np.ma.masked)
                #If more than one value with coordinates close enough is found, print terminated in csv and skip to next file
                elif len(lati) > 1 or len(longi) > 1:
                  row.append("Terminated")
                  writer.writerow(row)
                  raise LatLongError("Existence of two values with either latitude or longitude values within 0.01 degrees")
                else:
                  row.append(datapoint[timeio:timei,lati[0],longi[0]].mean())
              writer.writerow(row)
          except LatLongError as e:
              print e.value, "Skipping rest of file. Occured at ", filepath

      #Replace old output.csv with new csv (named temp but renamed to output)    
      os.remove(outputfileloc)
      os.rename(os.path.dirname(outputfileloc) + os.sep + "temp" + outputnum + ".csv", outputfileloc)
      #Release the netCDF4 file object
      rootgrp.close()
      printProgress(currentsize, totalsize, "Completed so far:", "Time taken: ", time.clock() - t0, time.clock() - t1)
      
    

