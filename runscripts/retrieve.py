import argparse
import os
import yaml
import logging
import numpy as np
import xarray as xr
from gsv.retriever import GSVRetriever
# from dinosaur import xarray_utils


def parse_args():
    """Parse command-line arguments."""
    parser = argparse.ArgumentParser(description="Retrieve GSV data")
    parser.add_argument(
        "--requests", "-c", type=str, default="request.yaml",
        help="Path to the request folder or file"
    )
    parser.add_argument(
        "--output", "-o", type=str, default="output",
        help="Path to the output folder"
    )
    parser.add_argument(
        "--translator", type=str, default="False",
        help="File to translate variables"
    )
    return parser.parse_args()


def load_request(request_path):
    """Load a YAML request file."""
    with open(request_path, "r") as file:
        return yaml.load(file, Loader=yaml.FullLoader)


def retrieve_data(gsv, mars_keys):
    """Retrieve data using GSVRetriever."""
    return gsv.request_data(mars_keys)


def save_data(data, output_path, filename):
    """Save data to a NetCDF file."""
    data.to_netcdf(os.path.join(output_path, filename))

def fix_sst(data):
    """ Add 273 to SST variable to convert to Kelvin """
    if "sea_surface_temperature" in data.variables:
        sst = data["sea_surface_temperature"]
        sst.attrs["units"] = "K"
        sst.values += 273.15
    return data

def estimate_ciwc_approximate(liquid_profile: xr.DataArray, total_ice: xr.DataArray) -> xr.DataArray:
    vertical_sum = liquid_profile.sum(dim="level")
    vertical_fraction = liquid_profile / vertical_sum.where(vertical_sum != 0, np.nan)
    specific_ice = total_ice * vertical_fraction
    return specific_ice.fillna(0)

def estimate_ciwc_constant(total_ice: xr.DataArray, level_dim: int) -> xr.DataArray:
    levels = np.arange(level_dim)
    return (total_ice / level_dim).expand_dims({"level": levels}).transpose("level", ...)

def interpolate_data(data, levels, method="constant"):
    """
    Interpolate or generate `specific_cloud_ice_water_content` (ciwc)
    from 2D data or interpolate 3D data to target levels.
    
    Args:
        data: xarray.Dataset containing the necessary input fields
        levels: list or array of vertical levels to interpolate to
        method: 'era5', 'approximate', or 'constant'
        era5_ds: xarray.Dataset with ERA5 data (required for 'era5' method)
        
    Returns:
        xarray.Dataset with sciwater_content interpolated to requested levels
    """
    logging.info("Interpolating data to specified levels")

    if "level" not in data.dims:
        logging.info("Adding level dimension to variable tciw")
        twod_data = data["tciw"]  # 2D: (time, lat, lon)
        time_dim, lat_dim, lon_dim = twod_data.shape
        new_shape = (time_dim, len(levels), lat_dim, lon_dim)

        if method == "approximate":
            threed_data = np.zeros(new_shape, dtype=np.float64)
            for t in range(time_dim):
                threed_data[t] = estimate_ciwc_approximate(
                    liquid_profile=data["clwc"][t],  # 3D: (level, lat, lon)
                    total_ice=data["tciw"][t]       # 2D: (lat, lon)
                ).values
        elif method == "constant":
            threed_data = np.zeros(new_shape, dtype=np.float64)
            for t in range(time_dim):
                threed_data[t] = estimate_ciwc_constant(
                    total_ice=data["tciw"][t], level_dim=len(levels)
                ).values
        else:
            raise ValueError(f"Unknown method '{method}'")

        ds_new = xr.Dataset({
            "specific_cloud_ice_water_content": (("time", "level", "lat", "lon"), threed_data)
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

    else:
        ds_new = data.interp(level=levels)

    return ds_new

def rename_variables(data, translator_file=None):
    """Rename variables based on standard names and translator file."""
    data_copy = data.copy()
    for var in data_copy.variables:
        if "standard_name" in data_copy[var].attrs:
            original_name = var
            standard_name = data_copy[var].attrs["standard_name"]
            renamed_name = standard_name if standard_name != "unknown" else original_name
            data_copy = data_copy.rename({var: renamed_name})

            if translator_file and renamed_name in translator_file:
                translated_name = translator_file[renamed_name]
                data_copy = data_copy.rename({renamed_name: translated_name})
    return data_copy

def build_iso_time(date, time) -> str:
    """
    Build an ISO 8601 datetime string from MARS-style date and time.
    Supports int or list input.

    Args:
        date (int or list): Date in YYYYMMDD format.
        time (int or list): Time in HHMM format.

    Returns:
        str: ISO 8601 datetime string (e.g., '1998-01-01T00:00')
    """
    if isinstance(date, list):
        date = date[0]
    if isinstance(time, list):
        time = time[0]

    date_str = str(date)
    time_str = f"{int(time):04d}"  # ensures 4-digit zero-padded string

    return f"{date_str[:4]}-{date_str[4:6]}-{date_str[6:]}T{time_str[:2]}:{time_str[2:]}"


def process_requests(requests_path, output_path, translator_path=None):
    """Process GSV data requests."""
    gsv = GSVRetriever()
    merged_dataset = xr.Dataset()
    translator_file = None

    if translator_path and os.path.exists(translator_path):
        translator_file = load_request(translator_path)

    for count, request_file in enumerate(os.listdir(requests_path)):
        logging.info(f"Processing request {request_file}")
        request = load_request(os.path.join(requests_path, request_file))
        mars_keys = request["mars-keys"]
        data = retrieve_data(gsv, mars_keys)

        # mars_keys.date = 19980101
        # mars_keys.time = 0000
        start_time = build_iso_time(mars_keys["date"], mars_keys["time"])
        end_time = start_time

        save_data(data, output_path, f"raw-{count}.nc")

        if "levelist_interpol" in request:
            levels = request["levelist_interpol"]
            data = interpolate_data(data, levels)

        data = rename_variables(data, translator_file)
        # data = fix_sst(data)
        #data = time_shift_and_slice(data, start_time, end_time)
        save_data(data, os.path.join(output_path, ".."), f"interpol-{count}.nc")
        merged_dataset = xr.merge([merged_dataset, data], compat="override")

    # transpose the merged dataset
    merged_dataset = merged_dataset.transpose("time", "level", "longitude", "latitude")
    merged_dataset.to_zarr(output_path)


def main():
    """Main function."""
    args = parse_args()
    logging.basicConfig(level=logging.DEBUG)
    process_requests(args.requests, args.output, args.translator)


if __name__ == "__main__":
    main()
