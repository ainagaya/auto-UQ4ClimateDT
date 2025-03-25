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
    return parser.parse_args()


def process_requests(requests_path, output_path):
    """Process GSV data requests."""
    gsv = GSVRetriever()

    count = 0

    # initialize empty xarray dataset
    merged_dataset = xarray.Dataset()

    for request in os.listdir(requests_path):
        logging.info(f"Processing request {request}")
        try:
            request = yaml.load(open(f"{requests_path}/{request}"), Loader=yaml.FullLoader)
            mars_keys = request["mars-keys"]
            data = gsv.request_data(mars_keys)
        except Exception as e:
            logging.warning(f"Failed to retrieve data for request {request}")
            continue
        logging.info("Raw data:", data)

        # data.to_netcdf(f"{output_path}/raw-{count}.nc")

        if "levelist_interpol" in request:
            levels = request.levelist_interpol
            data_interp = data.interp(level=levels)
            logging.info("Interpolated data:", data_interp)
        else:
            data_interp = data

        for var in data.variables:
            if "standard_name" in data[var].attrs:
                # Rename variables to standard names
                data_interp = data_interp.rename({var: data[var].attrs["standard_name"]})
                # plot the variable and save it in png format
                # data_interp[data[var].attrs["standard_name"]].plot().get_figure().savefig(f"{output_path}/{data[var].attrs['standard_name']}-{count}.png")

        # Uncomment the following line to save as Zarr format -> need contianer
        # data_interp.to_zarr("interpol.zarr")
        # data_interp.to_netcdf(f"{output_path}/interpol-{count}.nc")

        # Store all the data into a single file
        merged_dataset = xarray.merge([merged_dataset, data_interp], compat='override')

        count += 1

    merged_dataset.to_zarr(f"{output_path}")
    # merged_dataset.to_netcdf(f"{output_path}/merged.nc")


def main():
    """Main function."""
    args = parse_args()
    process_requests(args.requests, args.output)


if __name__ == "__main__":
    main()
