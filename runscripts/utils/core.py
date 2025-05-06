import argparse
import os
import yaml
import logging
import xarray as xr
from gsv.retriever import GSVRetriever

def parse_args():
    parser = argparse.ArgumentParser(description="Retrieve GSV data")
    parser.add_argument("--requests", "-c", type=str, default="request.yaml",
                        help="Path to the request folder or file")
    parser.add_argument("--output", "-o", type=str, default="output",
                        help="Path to the output folder")
    parser.add_argument("--translator", type=str, default="False",
                        help="File to translate variables")
    parser.add_argument("--postprocess", action="store_true",
                        help="Whether to perform postprocessing")
    return parser.parse_args()

def load_request(request_path):
    with open(request_path, "r") as file:
        return yaml.load(file, Loader=yaml.FullLoader)

def retrieve_data(gsv, mars_keys):
    return gsv.request_data(mars_keys)

def save_data_netcdf(data, output_path, filename):
    os.makedirs(output_path, exist_ok=True)
    data.to_netcdf(os.path.join(output_path, filename))

def build_iso_time(date, time) -> str:
    if isinstance(date, list):
        date = date[0]
    if isinstance(time, list):
        time = time[0]
    date_str = str(date)
    time_str = f"{int(time):04d}"
    return f"{date_str[:4]}-{date_str[4:6]}-{date_str[6:]}T{time_str[:2]}:{time_str[2:]}"
