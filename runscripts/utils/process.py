import os
import xarray as xr
import logging
from gsv.retriever import GSVRetriever
from utils.core import load_request, retrieve_data, save_data_netcdf, build_iso_time
from utils.interpolate import interpolate_data
from utils.postprocess import rename_variables

def process_requests(requests_path, output_path, translator_path=None, do_postprocessing=True):
    gsv = GSVRetriever()
    merged_dataset = xr.Dataset()
    translator_file = None
    clwc_store = []

    if translator_path and os.path.exists(translator_path):
        translator_file = load_request(translator_path)

    for count, request_file in enumerate(os.listdir(requests_path)):
        logging.info(f"Processing request {request_file}")
        request = load_request(os.path.join(requests_path, request_file))
        mars_keys = request["mars-keys"]
        data = retrieve_data(gsv, mars_keys)

        start_time = build_iso_time(mars_keys["date"], mars_keys["time"])
        end_time = start_time

        save_data_netcdf(data, output_path, f"raw-{count}.nc")

        if do_postprocessing:
            if "levelist_interpol" in request:
                levels = request["levelist_interpol"]
                data = interpolate_data(data, levels, clwc_store, method="approximate")

            if "clwc" in data:
                clwc_store = data["clwc"]

            data = rename_variables(data, translator_file)
            save_data_netcdf(data, os.path.join(output_path, ".."), f"interpol-{count}.nc")

        merged_dataset = xr.merge([merged_dataset, data], compat="override")


    if do_postprocessing:
        merged_dataset = merged_dataset.transpose("time", "level",  "latitude", "longitude")
        merged_dataset.to_zarr(output_path)

    return merged_dataset
