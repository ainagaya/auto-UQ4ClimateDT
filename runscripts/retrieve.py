import argparse
import os
import yaml
import logging
import numpy as np
import xarray
from gsv.retriever import GSVRetriever


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


def interpolate_data(data, levels):
    """Interpolate data to specified levels."""
    logging.info("Interpolating data to specified levels")
    if "level" not in data.dims:
        logging.info("Adding level dimension to variable tciw")
        # TODO GENERALIZE FOR VARIABLES
        twod_data = data["tciw"]
        print(twod_data)
        time_dim, lat_dim, lon_dim = twod_data.shape  # Get dimensions
        print(time_dim, lat_dim, lon_dim)
        new_shape = (time_dim, len(levels), lat_dim, lon_dim)
        threed_data = np.zeros(new_shape, dtype=np.float64)
        threed_data[:,0,:,:] = twod_data
        ds_new = xarray.Dataset({
            "tciw": (("time", "level", "lat", "lon"), threed_data)
        }, coords={
            "time": data["time"],
            "level": levels,
            "lat": data["lat"],
            "lon": data["lon"]
        })
        # Add attributes from original data
        #ds_new["tciw"].attrs.update(data["tciw"].attrs)
        ds_new["tciw"].attrs = data["tciw"].attrs.copy()

        #zero_layer = xarray.full_like(data.expand_dims(dim="level"), fill_value=0)
        #data = xarray.concat([zero_layer, data.expand_dims(dim="level")], dim="level")
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


def process_requests(requests_path, output_path, translator_path=None):
    """Process GSV data requests."""
    gsv = GSVRetriever()
    merged_dataset = xarray.Dataset()
    translator_file = None

    if translator_path and os.path.exists(translator_path):
        translator_file = load_request(translator_path)

    for count, request_file in enumerate(os.listdir(requests_path)):
        logging.info(f"Processing request {request_file}")
        request = load_request(os.path.join(requests_path, request_file))
        mars_keys = request["mars-keys"]
        data = retrieve_data(gsv, mars_keys)
        save_data(data, output_path, f"raw-{count}.nc")

        if "levelist_interpol" in request:
            levels = request["levelist_interpol"]
            data = interpolate_data(data, levels)

        data = rename_variables(data, translator_file)
        save_data(data, os.path.join(output_path, ".."), f"interpol-{count}.nc")
        merged_dataset = xarray.merge([merged_dataset, data], compat="override")

    merged_dataset.to_zarr(output_path)


def main():
    """Main function."""
    args = parse_args()
    logging.basicConfig(level=logging.DEBUG)
    process_requests(args.requests, args.output, args.translator)


if __name__ == "__main__":
    main()
