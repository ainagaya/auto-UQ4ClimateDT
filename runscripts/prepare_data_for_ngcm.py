"""
Open zarr and process it to match the format of the NGCM data

"""

import xarray as xr
import argparse
import logging
import yaml
import numpy as np
import os

from dinosaur import horizontal_interpolation
from dinosaur import spherical_harmonic
from dinosaur import xarray_utils

import neuralgcm
import jax
import pickle

def parse_args():
    """Parse command-line arguments."""
    parser = argparse.ArgumentParser(description="Retrieve GSV data")
    parser.add_argument(
        "--zarr", "-z", type=str, default="output",
        help="Path to the output folder"
    )
    return parser.parse_args()


args = parse_args()
data = xr.open_zarr("args.zarr")

full_era5_grid = spherical_harmonic.Grid(
    latitude_nodes=data.sizes['latitude'],
    longitude_nodes=data.sizes['longitude'],
    latitude_spacing=xarray_utils.infer_latitude_spacing(data.latitude),
    longitude_offset=xarray_utils.infer_longitude_offset(data.longitude),
)

model_checkpoint = 

with open(model_checkpoint, 'rb') as f:
  ckpt = pickle.load(f)

model = neuralgcm.PressureLevelModel.from_checkpoint(ckpt)

# Other available regridders include BilinearRegridder and NearestRegridder.
regridder = horizontal_interpolation.ConservativeRegridder(
    full_era5_grid, model.data_coords.horizontal, skipna=True
)

regridded = xarray_utils.regrid(data, regridder)

# fill nans
regridded_and_filled = xarray_utils.fill_nan_with_nearest(regridded)

# model.data_to_xarray(
#     model.inputs_from_xarray(regridded_and_filled),
#     times=None,  # times=None indicates no leading time-axis
# )