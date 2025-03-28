import argparse
import os
import yaml
from gsv.retriever import GSVRetriever
import xarray

import logging

def parse_args():
    """Parse command-line arguments."""
    parser = argparse.ArgumentParser(description="Retrieve GSV data")
    parser.add_argument(
        "--requests", "-c", type=str, default="request.yaml",
        help="Path to the request folder or file")
    parser.add_argument(
        "--output", "-o", type=str, default="output",
        help="Path to the output folder"
    )
    parser.add_argument('--translator', type=str, default="False", help='File to translate variables')
    return parser.parse_args()


def process_requests(requests_path, output_path, translator=False):
    """Process GSV data requests."""
    gsv = GSVRetriever()

    count = 0

    # initialize empty xarray dataset
    merged_dataset = xarray.Dataset()

    for request in os.listdir(requests_path):
        logging.info(f"Processing request {request}")
        try:
            request = yaml.load(open(f"{requests_path}/{request}"), Loader=yaml.FullLoader)
            logging.debug(f"Request: {request}")
            mars_keys = request["mars-keys"]
            logging.debug(f"Mars keys: {mars_keys}")
            data = gsv.request_data(mars_keys)
            logging.info(f"Data retrieved for request {request}")
        except Exception as e:
            logging.warning(f"Failed to retrieve data for request {request}")
            continue
        logging.info("Raw data:", data)

        # data.to_netcdf(f"{output_path}/raw-{count}.nc")

        if "levelist_interpol" in request:
            # if data doesn't have the dimension "level", create it, filling it with 0
            levels = request["levelist_interpol"]
            if "level" not in data.dims:
                zero_layer = xarray.full_like(data.expand_dims(dim="level"), fill_value = 0)
                #data = data.expand_dims("level")
                # Initialize with NaN (or another default value)
                #data = data.assign_coords(level=("level", levels))
                #data["level"] = [0]  # First level index for the 2D values
                # Fill the first level with the original data and the rest with 1
                #data = data.broadcast_like(data.expand_dims(level=levels))
                # for i, level in enumerate(levels):
                #     if i == 0:
                #         data.loc[{"level": level}] = data.isel(level=0)
                #     else:
                #         data.loc[{"level": level}] = 1
                data = xarray.concat([zero_layer, data.expand_dims(dim="level")], dim="level")
            else:
                data_interp = data.interp(level=levels)
            logging.info("Interpolated data:", data_interp)
        else:
            data_interp = data

        for var in data_interp.variables:
            logging.debug(f"Variable: {var}")
            if "standard_name" in data_interp[var].attrs:
                original_name = var
                # Rename variables to standard names
                # if the standard name is not unknown
                if data_interp[var].attrs["standard_name"] == "unknown":
                    renamed_name = var
                else:
                    renamed_name = data_interp[var].attrs["standard_name"]
                
                data_interp = data_interp.rename({var: renamed_name})
                logging.debug(f"Renamed {original_name} to {renamed_name}")

                if translator:
                    translator_file = yaml.load(open(translator), Loader=yaml.FullLoader)
                    # if that variable is in the translator file
                    if renamed_name in translator_file:
                        translated_name = translator_file[renamed_name]
                        logging.debug(f"Translating {renamed_name} to {translated_name}")
                        data_interp = data_interp.rename({renamed_name: translated_name})
                    else:
                        logging.debug(f"Variable {renamed_name} not in translator file")
                        continue
                # plot the variable and save it in png format
                # data_interp[data[var].attrs["standard_name"]].plot().get_figure().savefig(f"{output_path}/{data[var].attrs['standard_name']}-{count}.png")

        # Uncomment the following line to save as Zarr format -> need contianer
        # data_interp.to_zarr("interpol.zarr")
        data_interp.to_netcdf(f"{output_path}/../interpol-{count}.nc")

        # Store all the data into a single file
        merged_dataset = xarray.merge([merged_dataset, data_interp], compat='override')

        count += 1

    merged_dataset.to_zarr(f"{output_path}")
    # merged_dataset.to_netcdf(f"{output_path}/merged.nc")


def main():
    """Main function."""
    args = parse_args()
    # set log level to debug
    logging.basicConfig(level=logging.DEBUG)
    process_requests(args.requests, args.output, args.translator)


if __name__ == "__main__":
    main()
