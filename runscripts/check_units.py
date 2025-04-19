import xarray as xr

# Open the Zarr file
ds = xr.open_zarr("/gpfs/scratch/ehpc204/bsc032376/ics/fdb/neuralgcm/models_v1_stochastic_1_4_deg.pkl/20210101-20210103", consolidated=True)

# Inspect available variables
print(ds.data_vars)

# Check the units of geopotential
print(ds["geopotential"].attrs.get("units", "No units attribute found"))
