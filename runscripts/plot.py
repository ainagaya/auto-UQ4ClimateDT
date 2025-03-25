import xarray
import numpy as np
import matplotlib.pyplot as plt
import zarr

# open zarr
path = "/gpfs/scratch/bsc32/bsc032376/tfm/fdb/neuralgcm/models_v1_stochastic_1_4_deg.pkl/20210101-20210111"
ds = xarray.open_zarr(path)

# list variables
print(ds)

""""Data variables:
    air_temperature          (forecast_reference_time, level, ncells) float64 466MB dask.array<chunksize=(1, 5, 49152), meta=np.ndarray>
    eastward_wind            (forecast_reference_time, level, ncells) float64 466MB dask.array<chunksize=(1, 5, 49152), meta=np.ndarray>
    geopotential             (forecast_reference_time, level, ncells) float64 466MB dask.array<chunksize=(1, 5, 49152), meta=np.ndarray>
    northward_wind           (forecast_reference_time, level, ncells) float64 466MB dask.array<chunksize=(1, 5, 49152), meta=np.ndarray>
    specific_humidity        (forecast_reference_time, level, ncells) float64 466MB dask.array<chunksize=(1, 5, 49152), meta=np.ndarray>
"""

ds.air_temperature.plot()
plt.savefig("air_temperature.png")
plt.clf()

ds.eastward_wind.plot()
plt.savefig("eastward_wind.png")
plt.clf()

ds.geopotential.plot()
plt.savefig("geopotential.png")
plt.clf()

ds.northward_wind.plot()
plt.savefig("northward_wind.png")
plt.clf()

ds.specific_humidity.plot()
plt.savefig("specific_humidity.png")
plt.clf()
