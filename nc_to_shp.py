import numpy as np
import csv
from netCDF4 import Dataset

rootgrp = Dataset("C:/Github/WS10_VCSN_xaijz_2006-2010c0.nc", "r", format="NETCDF4")
var = rootgrp["ws10"]
lat = rootgrp["latitude"][:]
long = rootgrp["longitude"][:]
time = rootgrp["time"][:]

csvfile = open("C:/Github/table.csv", "rb")
reader = csv.reader(csvfile)
outputfile = open("c:/Github/output.csv", "wb")
writer = csv.writer(outputfile)
row = reader.next()
row.append("var")
writer.writerow(row)
for row in reader:
	# latitude index
	print row
	lati = np.argmin(np.abs(lat - np.float32(row[2])))
	# longitude index
	longi = np.argmin(np.abs(long - np.float32(row[3])))
	print "H"
	row.append(var[1][lati][longi])
	writer.writerow(row)

csvfile.close()
outputfile.close()

