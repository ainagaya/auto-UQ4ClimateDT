import numpy as np
import xarray as xr
import logging

def estimate_ciwc_approximate(liquid_profile: xr.DataArray, total_ice: xr.DataArray) -> xr.DataArray:
    liquid_profile = liquid_profile.astype("float32").fillna(0.0)
    total_ice = total_ice.astype("float32")
    vertical_sum = liquid_profile.sum(dim="level")
    vertical_fraction = liquid_profile / xr.where(vertical_sum > 1e-6, vertical_sum, np.nan)
    specific_ice = total_ice * vertical_fraction
    return specific_ice.fillna(0.0).clip(min=0.0) / 400

def estimate_ciwc_constant(total_ice: xr.DataArray, level_dim: int) -> xr.DataArray:
    levels = np.arange(level_dim)
    return (total_ice / level_dim).expand_dims({"level": levels}).transpose("level", ...)

def interpolate_data(data, levels, clwc_store, method="approximate"):
    logging.info("Interpolating data to specified levels")

    if "level" not in data.dims:
        twod_data = data["tciw"]
        time_dim, lon_dim, lat_dim = twod_data.shape
        new_shape = (time_dim, lon_dim, lat_dim, len(levels))

        threed_data = np.zeros(new_shape, dtype=np.float64)
        for t in range(time_dim):
            if method == "approximate":
                threed_data[t] = estimate_ciwc_approximate(
                    liquid_profile=clwc_store[t],
                    total_ice=data["tciw"][t]
                ).values
            elif method == "constant":
                threed_data[t] = estimate_ciwc_constant(
                    total_ice=data["tciw"][t],
                    level_dim=len(levels)
                ).values
            else:
                raise ValueError(f"Unknown method '{method}'")

        ds_new = xr.Dataset({
            "specific_cloud_ice_water_content": ("time", "lat", "lon", "level", threed_data)
        }, coords={
            "time": data["time"],
            "level": levels,
            "lat": data["lat"],
            "lon": data["lon"]
        })

        ds_new["specific_cloud_ice_water_content"].attrs = {
            "units": "kg/kg",
            "long_name": "specific_cloud_ice_water_content"
        }

        return ds_new.chunk({"level": 37, "lat": 180, "lon": 360})

    return data.interp(level=levels)
