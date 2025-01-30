import xarray as xr
import matplotlib.pyplot as plt

import argparse


import cartopy.crs as ccrs
import cartopy

parser = argparse.ArgumentParser(description="Compare two grib files")
parser.add_argument("--grib1", type=str, help="Path to the first grib file")
parser.add_argument("--grib2", type=str, help="Path to the second grib file")
args = parser.parse_args()

grib1 = xr.load_dataset(args.grib1, engine="cfgrib")
grib2 = xr.load_dataset(args.grib2, engine="cfgrib")

# compare q values over the globe
fig, ax = plt.subplots(1, 2, subplot_kw={"projection": ccrs.PlateCarree()})
grib1.q.isel(time=-1).plot(ax=ax[0], transform=ccrs.PlateCarree())
grib2.q.isel(time=-1).plot(ax=ax[1], transform=ccrs.PlateCarree())
ax[0].coastlines()
ax[1].coastlines()
plt.savefig("q_comparison.png")

