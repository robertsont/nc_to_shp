import sys
from cx_Freeze import setup, Executable

setup(
    name = "nc_to_shp",
    version = "1.0",
    description = "Tool for reading in data from large collection of netCDF4 files to a csv using longitude and latitude coordinates.",
    options = {"build_exe": {"includes": [], "include_files": [], "packages": ["netCDF4", "netcdftime"]}},
    executables = [Executable("nc_to_shp.py")]
    )
