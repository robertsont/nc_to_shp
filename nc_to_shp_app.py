exec(open("nc_to_shpv9.py").read())

table_loc = "T:\\Auckland\\Projects A-E\\EPD GIS\\Shared\\Project\\CCII\\climate_data_csvs\\processing\\table.csv"
output_loc = "T:\\Auckland\\Projects A-E\\EPD GIS\\Shared\\Project\\CCII\\climate_data_csvs\\processing\\outputtemp.csv"

if __name__ == "__main__":
  timeslice = int(input("Please enter a time range: "))
  runDataAvg(table_loc, output_loc, timeslice, "X:\\Hamilton\\SpatialLabBaseData\\NZ\\Climate\\CCII\\Ann")
  input("Finished")


