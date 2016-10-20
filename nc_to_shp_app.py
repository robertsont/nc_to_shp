import nc_to_shpv9 as nc

if __name__ == "__main__":
  timeslice = int(input("Please enter a time range: "))
  nc.runDataAvg("C:\\Github\\NetCDF4 file reader\\nc_to_shp\\table.csv", "C:\\Github\\NetCDF4 file reader\\nc_to_shp\\output.csv", timeslice, "X:\\Hamilton\\SpatialLabBaseData\\NZ\\Climate\\CCII")
  input("Finished")


