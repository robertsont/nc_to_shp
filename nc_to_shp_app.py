import nc_to_shpv6 as nc
import multiprocessing as mp

if __name__ == "__main__":
  #queue = mp.Queue()
  timeslice = int(raw_input("Please enter a time range: "))
  #p = mp.Pool(processes=4)
  nc.runDataAvg("C:\\Github\\nc_to_shp\\table.csv", "C:\\Github\\nc_to_shp\\output.csv", "C:\\Github\\nc_to_shp\\temp.csv", timeslice, "X:\\Hamilton\\SpatialLabBaseData\\NZ\\Climate\\CCII\\RCP2.6")
  #p.apply_async(nc.runDataAvg, ("C:\\Github\\nc_to_shp\\table.csv", "C:\\Github\\nc_to_shp\\output1.csv", "C:\\Github\\nc_to_shp\\temp1.csv", timeslice, "X:\\Hamilton\\SpatialLabBaseData\\NZ\\Climate\\CCII\\RCP4.5",))  
  #p.apply_async(nc.runDataAvg, ("C:\\Github\\nc_to_shp\\table.csv", "C:\\Github\\nc_to_shp\\output2.csv", "C:\\Github\\nc_to_shp\\temp2.csv", timeslice, "X:\\Hamilton\\SpatialLabBaseData\\NZ\\Climate\\CCII\\RCP6.0",))
  #p.apply_async(nc.runDataAvg, ("C:\\Github\\nc_to_shp\\table.csv", "C:\\Github\\nc_to_shp\\output3.csv", "C:\\Github\\nc_to_shp\\temp3.csv", timeslice, "X:\\Hamilton\\SpatialLabBaseData\\NZ\\Climate\\CCII\\RCP8.5",))  
  raw_input("Finished")
#[os.system("start cmd /K python nc_to_shpv6.py " + `i` + " C:\\Github\\nc_to_shp\\table.csv C:\\Github\\nc_to_shp\\output " + timeslice + " X:\\Hamilton\\SpatialLabBaseData\\NZ\\Climate\\CCII\\") for i in range(0,1)]

