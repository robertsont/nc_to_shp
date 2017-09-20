import sys, os, time, csv
from collections import deque
import numpy as np
from netCDF4 import Dataset, num2date
import scipy.io.netcdf as scinet

relativepath = "X:\\Hamilton\\SpatialLabBaseData\\NZ\\Climate\\CCII\\RCP2.6"

for subdir, dirs, files in os.walk(relativepath):
    for filename in files:
        print(subdir.split('\\')[subdir.split('\\').index('CCII')+1])
