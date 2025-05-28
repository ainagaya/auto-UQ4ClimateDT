import os
import pickle
import logging
import argparse
from datetime import datetime, timedelta

import numpy as np
import xarray
import cftime
import jax

from dinosaur import horizontal_interpolation, spherical_harmonic, xarray_utils
import neuralgcm

from functions import parse_arguments, read_config, define_variables

# Configure logging
logging.basicConfig(level=logging.DEBUG)

def validate_config(config):
    required_keys = [
        'model_checkpoint', 'INI_DATA_PATH', 'start_time',
        'end_time', 'data_inner_steps', 'inner_steps'
    ]
    for key in required_keys:
        if key not in config:
            raise ValueError(f'Missing required config key: {key}')

def time_shift(ds: xarray.Dataset, start_time: str, end_time: str) -> xarray.Dataset:
    """
    Applies a 24-hour time shift to forcing variables and slices the dataset.
    """
    shifted = (
        ds.pipe(
            xarray_utils.selective_temporal_shift,
            variables=model.forcing_variables,
            time_shift='24 hours'
        )
        .sel(time=slice(start_time, end_time))
        .compute()
    )
    return shifted

# === Main Script === #

args = parse_arguments()
config = read_config(args.config)
validate_config(config)

(model_checkpoint, INI_DATA_PATH, start_time, end_time,
 data_inner_steps, inner_steps, rng_key, output_path) = define_variables(config)

logging.info(f"Config loaded with start_time: {start_time}, end_time: {end_time}")

#start_date = datetime.strptime(start_time, '%Y-%m-%d') + timedelta(days=1)
start_date = datetime.strptime(start_time, '%Y-%m-%d')
# input_end_date = datetime.strptime(start_time, '%Y-%m-%d') + timedelta(days=2)
input_end_date = datetime.strptime(start_time, '%Y-%m-%d') + timedelta(days=1)
end_date = datetime.strptime(end_time, '%Y-%m-%d')

days_to_run = (end_date - start_date).days + 1
outer_steps = days_to_run * 24 // inner_steps
delta_t = np.timedelta64(inner_steps, 'h')
times = np.arange(outer_steps) * inner_steps  # in hours

# Load model
with open(model_checkpoint, 'rb') as f:
    ckpt = pickle.load(f)
model = neuralgcm.PressureLevelModel.from_checkpoint(ckpt)

# Load and shift data
data_original = xarray.open_zarr(INI_DATA_PATH, chunks=None)
data_shift = time_shift(data_original, start_time, input_end_date)

# Setup grid and regridder
data_grid = spherical_harmonic.Grid(
    latitude_nodes=data_shift.sizes['latitude'],
    longitude_nodes=data_shift.sizes['longitude'],
    latitude_spacing=xarray_utils.infer_latitude_spacing(data_shift.latitude),
    longitude_offset=xarray_utils.infer_longitude_offset(data_shift.longitude),
)
regridder = horizontal_interpolation.ConservativeRegridder(
    data_grid, model.data_coords.horizontal, skipna=True
)

# Regrid and fill NaNs
regridded = xarray_utils.regrid(data_shift, regridder)
data = xarray_utils.fill_nan_with_nearest(regridded)

# Convert time coordinates
# calendar = "proleptic_gregorian"
# new_reference = cftime.DatetimeProlepticGregorian(1900, 1, 1)

# decoded_times = [
#     cftime.DatetimeProlepticGregorian(
#         int(y), int(m), int(d)
#     ) for y, m, d in zip(data.time.dt.year.values, data.time.dt.month.values, data.time.dt.day.values)
# ]
# new_time_hours = np.array([
#     (t - new_reference).total_seconds() / 3600 for t in decoded_times
# ])

# data['time'] = ('time', new_time_hours)
# data['time'].attrs.update({
#     'units': 'hours since 1900-01-01',
#     'calendar': calendar
# })
# data['time'].encoding.update({
#     'dtype': 'float64',
#     '_FillValue': None
# })

# Save regridded data
data.to_zarr(f"{INI_DATA_PATH}/regridded", mode="w")
data.to_netcdf(f"{INI_DATA_PATH}/regridded.nc")

# Prepare inputs and forcings
inputs = model.inputs_from_xarray(data.isel(time=0))
input_forcings = model.forcings_from_xarray(data.isel(time=0))
initial_state = model.encode(inputs, input_forcings, rng_key)
all_forcings = model.forcings_from_xarray(data.head(time=1))

# Forecast
final_state, predictions = model.unroll(
    initial_state,
    all_forcings,
    steps=outer_steps,
    timedelta=delta_t,
    start_with_input=True,
)

# Convert predictions to xarray
predictions_ds = model.data_to_xarray(predictions, times=times)
# predictions_ds = model.data_to_xarray(predictions)

# Ensure output path exists
os.makedirs(output_path, exist_ok=True)

# Save outputs
with open(f"{output_path}/model_state-{start_time}-{end_time}-{rng_key}.pkl", "wb") as f:
    pickle.dump(final_state, f)

try:
    predictions_ds.to_netcdf(f"{output_path}/model_state-{start_time}-{end_time}-{rng_key}.nc")
except Exception as e:
    logging.warning(f"NetCDF save failed: {e}, trying Zarr...")
    try:
        predictions_ds.to_zarr(f"{output_path}/model_state-{start_time}-{end_time}-{rng_key}.zarr", mode="w")
    except Exception as e2:
        logging.error(f"Zarr save failed too: {e2}")
