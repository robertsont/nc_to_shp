import os
import sys
import numpy as np
import csv
import time
from netCDF4 import Dataset, num2date
import psutil
import math

#Error class for use when two values are have coordinates that are
#too close to distinguish as different points
class LatLongError(Exception):
  def __init__(self, value):
    self.value = value
  def __str__(self):
    return repr(self.value)

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

def writeTopRow(row, timeslice, varTitle, years, filename):
  #Final element is terminated with a carriage return character and new line character, so remove these two characters (\r\n)
  row[len(row)-1] = row[len(row)-1][:-2]
  #Place variable name as first element in new column
  row.append(filename[:-3] + "_" + varTitle)
  numberOfYears =  len(set(years))/(timeslice)+(len(set(years))%timeslice != 0)
  if len(set(years)) > timeslice:
    row = row + [`(years[0]+(timeslice)*(x-1))` + "-" + `(years[0]+(timeslice)*x-1)` for x in range(2,numberOfYears)] + [`(years[0]+(timeslice)*(numberOfYears-1))` + "-" + `years[years.size-1]`] # for x in range(0, len(set(years))%(timeslice) != 0)]
  return row, numberOfYears

def fileReadWrite(datapoint, lats, longs, fileloc, tempfile, timeslice, years, varTitle, filename):
  with open(fileloc, "rb") as inputfile:
    with open(tempfile, "wb") as outputfile:
      writer = csv.writer(outputfile)
      row, numberOfYears = writeTopRow(inputfile.next().split(","), timeslice, varTitle, years, filename)
      writer.writerow(row)
      length = len(lats)
      savedvalues = [[[0 for x in range(len(longs))] for y in range(length)] for z in range(numberOfYears)]
      buffersize = int(math.ceil(float(datapoint.size)*128/psutil.virtual_memory()[1])) + 1
      for i in range(0, buffersize, 1):
        try:
          datapoint1 = datapoint[:,length*i/buffersize:length*(1+i)/buffersize,:]
          inputfile.next() 
          for row in inputfile:
            row = row.split(",")
            row[len(row)-1] = row[len(row)-1][:-2]
            lati = np.argwhere(np.abs(lats - np.float32(row[2]))< 0.01)[0,0]
            longi = np.argwhere(np.abs(longs - np.float32(row[3]))< 0.01)[0,0]
            if lati < length*i/buffersize or lati >= length*(i+1)/buffersize:
              if i == buffersize-1:
                row = row + [savedvalues[0][lati][longi]]
                writer.writerow(row)
              continue
            timej = 0
            for j in range(0,numberOfYears):
              timejo = timej
              year = years[timejo]
              try:
                timej = np.argwhere(years == years[timejo]+timeslice)[0][0]
              except IndexError:
                timej=years.size
              savedvalues[j][lati][longi] = datapoint1[timejo:timej,lati-length*i/buffersize,longi].mean()
              row.append(savedvalues[j][lati][longi])
            if i==buffersize-1: 
              writer.writerow(row)
          inputfile.seek(0)
        except LatLongError as e:
          print e.value, "Skipping rest of file. Occured at ", filepath

def extractData(filepath):
  t3 = time.clock()
  rootgrp = Dataset(filepath, "r", format="NETCDF4", diskless=True)
  return rootgrp, rootgrp["latitude"][:], rootgrp["longitude"][:], np.asarray([getattr(x, "year") for x in [num2date(y,rootgrp["time"].units) for y in rootgrp["time"][:]]]), time.clock()-t3

def runDataAvg(inputfileloc, outputfileloc, tempfile, timeslice, relativepath):
  #Boolean for determinig whether to read from table.csv or output.csv
  firstRead = True
  totalsize = getSize(relativepath)

  print "Directory size", totalsize/(1024*1024*1024), "GB"
  currentsize = 0
  printProgress(currentsize, totalsize, "Completed so far:",)

  t0 = time.clock()
  #Traverse through all files in all subdirectories in the path specified above
  for subdir, dirs, files in os.walk(relativepath):
    for filename in files:
      t1 = time.clock()
      filepath = os.path.join(subdir, filename)
      currentsize += os.path.getsize(filepath)
      #Only open netCDF4 files
      if filepath.endswith(".nc"):
        if firstRead:
          fileloc = inputfileloc
          firstRead = False
        else:
          fileloc = outputfileloc
        
        rootgrp, lats, longs, years, t3 = extractData(filepath)

        for var in iter(rootgrp.variables):		
          if var != "longitude" and var != "latitude" and var != "elevation" and var != "time_bnds" and var != "time":
            fileReadWrite(rootgrp[var], lats, longs, fileloc, tempfile, timeslice, years, var, filename)
         
        os.remove(outputfileloc)
        os.rename(tempfile, outputfileloc)
        rootgrp.close()
        printProgress(currentsize, totalsize, "Completed so far:", "Time taken: ", time.clock() - t0, time.clock() - t1, t3)
        
    

