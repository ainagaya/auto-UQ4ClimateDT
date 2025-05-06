import argparse
import os
import logging
from utils.core import parse_args, load_request, retrieve_data, save_data_netcdf
from utils.interpolate import interpolate_data
from utils.postprocess import rename_variables, fix_sst
from utils.process import process_requests
import xarray as xr
from shutil import copyfileobj

def save_data_grib(data, output_path, filename):
    os.makedirs(output_path, exist_ok=True)
    with open(os.path.join(output_path, filename), "wb") as grib_file:
        copyfileobj(data, grib_file)

def main():
    parser = argparse.ArgumentParser(description="Retrieve and process GSV data")
    parser.add_argument("--requests", "-c", type=str, default="request.yaml", help="Path to the request folder or file")
    parser.add_argument("--output", "-o", type=str, default="output", help="Path to the output folder")
    parser.add_argument("--translator", type=str, default=None, help="File to translate variables")
    parser.add_argument("--postprocess", action="store_true", help="Whether to perform postprocessing")
    parser.add_argument("--input-format", type=str, default="zarr", choices=["netcdf", "zarr", "grib"], help="Output format")
    args = parser.parse_args()

    logging.basicConfig(level=logging.DEBUG)
    ds = process_requests(args.requests, args.output, args.translator, args.postprocess)
    if args.output_format == "netcdf":
        save_data_netcdf(ds, args.output, "merged.nc")
    elif args.output_format == "zarr":
        ds.to_zarr(args.output)
    elif args.output_format == "grib":
        save_data_grib(ds, args.output, "merged.grib")



if __name__ == "__main__":
    main()
