import sys, os, time, csv
from collections import deque
import numpy as np
from netCDF4 import Dataset, num2date
import scipy.io.netcdf as scinet

# Print iterations progress
def printProgress (iteration, total, prefix = '', suffix = '', timetaken = 0, timerecent=0, filetime=0):
    formatStr = "{0:." + str(1) + "f}"
    percents = formatStr.format(100 * (iteration / float(total)))
    sys.stdout.write('\r%s %s%s %s %s %s %s %s %s' % (prefix, percents, '%', suffix, round(timetaken,2), "Last file:", round(timerecent,2), "File read:", round(filetime,2))),
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

def writeTopRow(row, timeslice, varTitle, years, filename, subdir):
  #Place variable name as first element in new column
  row.append(filename[:-3] + "_" + varTitle + "_" + subdir.split('\\')[subdir.split('\\').index('CCII')+1])
  #Based on timeslice, figure out the division of years for the file
  numberOfYears =  int(len(set(years))/(timeslice)+(len(set(years))%timeslice != 0))
  if len(set(years)) > timeslice:
    row = row + [str(years[0]+(timeslice)*(x-1)) + "-" + str(years[0]+(timeslice)*x-1) for x in list(range(2,numberOfYears))] + [str(years[0]+(timeslice)*(numberOfYears-1)) + "-" + str(years[years.size-1])] # for x in range(0, len(set(years))%(timeslice) != 0)]
  return row, numberOfYears

def fileReadWrite(datapoint, lats, longs, outputData, timeslice, years, varTitle, filename, subdir):
  row, numberOfYears = writeTopRow(outputData[0], timeslice, varTitle, years, filename, subdir)
  outputData[0] = row
  for outCount in range(1,len(outputData)):
    row = outputData[outCount]
    lati = np.argwhere(np.abs(lats - np.float32(row[2]))< 0.01)
    longi = np.argwhere(np.abs(longs - np.float32(row[3]))< 0.01)
    if len(lati) == 0 or len(longi) == 0:
      outputData[outCount] = outputData[outCount] + [np.ma.masked for k in range(0, numberOfYears)]
    else:
      timej = 0
      for j in range(0,numberOfYears):
        timejo = timej
        year = years[timejo]
        try:
          timej = np.argwhere(years == years[timejo]+timeslice)[0][0]
        except IndexError:
          timej=years.size
        outputData[outCount].append(datapoint[timejo:timej,lati[0][0],longi[0][0]].mean())
  return outputData
            
def extractData(filepath):
  rootgrp = scinet.netcdf_file(filepath, "r", False)
  return rootgrp, rootgrp.variables["latitude"][:].copy(), rootgrp.variables["longitude"][:].copy(), np.asarray([getattr(x, "year") for x in [num2date(y,rootgrp.variables["time"].units.decode('utf8')) for y in rootgrp.variables["time"][:]]])

def runDataAvg(inputfileloc, outputfileloc, timeslice, relativepath):
  #Boolean for determining whether to read from table.csv or output.csv
  totalsize = getSize(relativepath)
  log = []

  print("Directory size", totalsize/(1024*1024*1024), "GB")
  currentsize = 0
  printProgress(currentsize, totalsize, "Completed so far:",)
  outputData = deque()
  
  with open(inputfileloc, "r") as inputfile:
    counter = 0  
    for row in inputfile:
      row = row.split(',')
      row[len(row)-1] = row[len(row)-1][:-1]
      outputData.append(row)
  t0 = time.clock()
  #Traverse through all files in all subdirectories in the path specified above
  for subdir, dirs, files in os.walk(relativepath):
    for filename in files:
      t1 = time.clock()
      filepath = os.path.join(subdir, filename)
      currentsize += os.path.getsize(filepath)
      #Only open netCDF4 files
      if filepath.endswith(".nc"):
        try:
          t3 = time.clock()
          rootgrp, lats, longs, years = extractData(filepath)
          t3 = time.clock()-t3
          for var in iter(rootgrp.variables):
            if var != 'longitude' and var != 'latitude' and var != 'elevation' and var != 'time_bnds' and var != 'time' and var != 'x_index' and var != 'y_index' and var != 'time_bounds':
              try:
                outputData = fileReadWrite(rootgrp.variables[var][:,:,:].copy(), lats, longs, outputData, timeslice, years, var, filename, subdir)
              except (KeyError, IndexError) as e:
                log = log + [e, var, filename]
          rootgrp.close()
          printProgress(currentsize, totalsize, "Completed so far:", "Time taken: ", time.clock() - t0, time.clock() - t1, t3)

        except OverflowError as e:
          log = log + [e, filename]
  with open(outputfileloc, 'w+', newline='') as outputfile:
    writer = csv.writer(outputfile)
    for row in outputData:
      writer.writerow(row)
      
  print(log)
    

