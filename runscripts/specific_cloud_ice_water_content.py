import xarray as xr
import numpy as np
import argparse

def method_era5(ds_era5: xr.Dataset) -> xr.DataArray:
    """Use ERA5 field directly (cheating method)."""
    return ds_era5["specific_cloud_ice_water_content"]

def method_approximate_from_liquid_profile(
    liquid_profile: xr.DataArray,
    specific_liquid: xr.DataArray,
    total_ice: xr.DataArray
) -> xr.DataArray:
    """
    Approximate the vertical profile of specific cloud ice water content 
    using the vertical distribution of liquid water.
    
    Args:
        liquid_profile: 3D (lev x lat x lon) cloud liquid water content profile
        specific_liquid: 2D (lat x lon) specific cloud liquid water content at one level
        total_ice: 2D (lat x lon) total column cloud ice water

    Returns:
        3D specific cloud ice water content (lev x lat x lon)
    """
    vertical_sum = liquid_profile.sum(dim="level")
    vertical_fraction = liquid_profile / vertical_sum.where(vertical_sum != 0, np.nan)

    specific_ice = total_ice * vertical_fraction
    return specific_ice.fillna(0)

def method_constant_from_total(total_ice: xr.DataArray, shape: tuple) -> xr.DataArray:
    """
    Distribute total column ice evenly across levels.
    
    Args:
        total_ice: 2D (lat x lon) total column cloud ice water
        shape: tuple of (levels, lat, lon)
    
    Returns:
        3D (lev x lat x lon) constant specific ice water content
    """
    levels, lat, lon = shape
    return (total_ice / levels).broadcast_like(xr.DataArray(
        np.ones(shape),
        dims=("level", "latitude", "longitude"),
        coords={"level": np.arange(levels), 
                "latitude": total_ice.latitude, 
                "longitude": total_ice.longitude}
    ))

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--method", choices=["era5", "approximate", "constant"], required=True)
    parser.add_argument("--input", help="Path to input dataset (NetCDF)", required=True)
    parser.add_argument("--output", help="Path to save output NetCDF", required=True)
    parser.add_argument("--era5", help="Optional ERA5 dataset if using --method era5")
    args = parser.parse_args()

    ds = xr.open_dataset(args.input)

    if args.method == "era5":
        if not args.era5:
            raise ValueError("ERA5 dataset path required for method 'era5'")
        era5_ds = xr.open_dataset(args.era5)
        result = method_era5(era5_ds)

    elif args.method == "approximate":
        result = method_approximate_from_liquid_profile(
            ds["cloud_liquid_water_content"],  # 3D
            ds["specific_cloud_liquid_water_content"],  # 2D
            ds["total_column_cloud_ice_water"]  # 2D
        )

    elif args.method == "constant":
        levels = ds["cloud_liquid_water_content"].shape[0]
        shape = (levels, ds.dims["latitude"], ds.dims["longitude"])
        result = method_constant_from_total(ds["total_column_cloud_ice_water"], shape)

    result.name = "specific_cloud_ice_water_content"
    result.to_netcdf(args.output)

if __name__ == "__main__":
    main()
