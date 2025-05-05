
import jax
import numpy as np
import pickle
import xarray
import cftime

from dinosaur import horizontal_interpolation
from dinosaur import spherical_harmonic
from dinosaur import xarray_utils
import neuralgcm
import os

import argparse
import yaml
from datetime import datetime, timedelta

from functions import parse_arguments, read_config, define_variables

import logging

# Set logging level to DEBUG (for most detailed output)
logging.basicConfig(level=logging.DEBUG)

def validate_config(config):
    required_keys = ['model_checkpoint', 'INI_DATA_PATH', 'start_time', 'end_time', 'data_inner_steps', 'inner_steps']
    for key in required_keys:
        if key not in config:
            raise ValueError(f'Key {key} is missing from the config file')

def time_shift(ds: xarray.Dataset, start_time: str, end_time: str) -> xarray.Dataset:
    """
    Applies a 24-hour time shift to the forcing variables and slices the dataset
    to the specified range.

    Args:
        ds (xarray.Dataset): Input dataset.
        start_time (str): ISO start time (e.g., "1988-02-01").
        end_time (str): ISO end time (e.g., "1988-02-03").

    Returns:
        xarray.Dataset: Time-shifted and sliced dataset.
    """
    # Apply 24h shift to selected variables
    data_shift = (
        ds.pipe(
            xarray_utils.selective_temporal_shift,
            variables=model.forcing_variables,
            time_shift='24 hours',
        )
        .sel(time=slice(start_time, end_time))  # Remove the 3rd argument
        .compute()
    )
    return data_shift

args = parse_arguments()
config = read_config(args.config)
validate_config(config)
model_checkpoint, INI_DATA_PATH, start_time, end_time, data_inner_steps, inner_steps, rng_key, output_path = define_variables(config)

print("model_checkpoint", model_checkpoint)
print("INI_DATA_PATH", INI_DATA_PATH)
print("start_time", start_time)
print("end_time", end_time)
print("data_inner_steps", data_inner_steps)
print("inner_steps", inner_steps)
print("rng_key", rng_key)

start_date = datetime.strptime(start_time, '%Y-%m-%d') + timedelta(days=1)
print("start_date", start_date)

end_date = datetime.strptime(end_time, '%Y-%m-%d')
print("end_date", end_date)


days_to_run = (end_date - start_date).days
print("days_to_run", days_to_run)

outer_steps = days_to_run * 24 // inner_steps
print("outer_steps", outer_steps)

timedelta = np.timedelta64(1, 'h') * inner_steps
print("timedelta", timedelta)

times = (np.arange(outer_steps) * inner_steps)  # time axis in hours
print("times", times)

with open(model_checkpoint, 'rb') as f:
  ckpt = pickle.load(f)

model = neuralgcm.PressureLevelModel.from_checkpoint(ckpt)

print("model", model)

data_original = xarray.open_zarr(INI_DATA_PATH, chunks=None)

print("data_original", data_original)

data_shift = time_shift(data_original, start_time, end_time)

print("data_shift", data_shift)

# Flip latitude and longitude coordinates, to match ERA5 ???

data_grid = spherical_harmonic.Grid(
    latitude_nodes=data_shift.sizes['latitude'],
    longitude_nodes=data_shift.sizes['longitude'],
    latitude_spacing=xarray_utils.infer_latitude_spacing(data_shift.latitude),
    longitude_offset=xarray_utils.infer_longitude_offset(data_shift.longitude),
)

# Other available regridders include BilinearRegridder and NearestRegridder.
regridder = horizontal_interpolation.ConservativeRegridder(
    data_grid, model.data_coords.horizontal, skipna=True
)

#data_sliced = data_shift.sel(time=start_date).compute()

data_sliced = data_shift

regridded = xarray_utils.regrid(data_sliced, regridder)

data = xarray_utils.fill_nan_with_nearest(regridded)

# Define calendar and new reference date matching era 5
calendar = "proleptic_gregorian"
new_reference = cftime.DatetimeProlepticGregorian(1900, 1, 1)

# Reconstruct decoded times with the correct calendar
year = data.time.dt.year
month = data.time.dt.month
day = data.time.dt.day
decoded_times = [cftime.DatetimeProlepticGregorian(year, month, day) + np.timedelta64(i, 'D') for i in range(len(data.time))]

# Compute new time values in hours since reference
new_time_hours = np.array([(t - new_reference).total_seconds() / 3600 for t in decoded_times])
#new_time_hours = np.array(
#    [(t - new_reference).total_seconds() / 3600 for t in decoded_times],
#    dtype='int64'
#)

# Replace the time coordinate with new values and update attributes
data['time'] = ('time', new_time_hours)
data['time'].attrs['units'] = "hours since 1900-01-01"
data['time'].attrs['calendar'] = "proleptic_gregorian"
# Ensure correct encoding (double without FillValue)
data['time'].encoding.update({
    "dtype": "float64",
    "_FillValue": None  # Important: remove NaN fill value
})

# Save the regridded data to a new zarr file and a netcdf file
path_to_save_zarr = f"{INI_DATA_PATH}/regridded"
data.to_zarr(path_to_save_zarr, mode="w")
path_to_save_nc = f"{INI_DATA_PATH}/regridded.nc"
data.to_netcdf(path_to_save_nc)

start_date = datetime.strptime(start_time, '%Y-%m-%d')
print("start_date", start_date)

end_date = datetime.strptime(end_time, '%Y-%m-%d')
print("end_date", end_date)


days_to_run = (end_date - start_date).days
print("days_to_run", days_to_run)

outer_steps = days_to_run * 24 // inner_steps
print("outer_steps", outer_steps)

timedelta = np.timedelta64(1, 'h') * inner_steps
print("timedelta", timedelta)

times = (np.arange(outer_steps) * inner_steps)  # time axis in hours
print("times", times)

print("Will run for", outer_steps, "steps")

print("initialize model state")

print("data at line 178", data)

inputs = model.inputs_from_xarray(data.isel(time=0))
print("inputs", inputs)
input_forcings = model.forcings_from_xarray(data.isel(time=0))
print("input_forcings", input_forcings)
initial_state = model.encode(inputs, input_forcings, rng_key)
print("initial_state", initial_state)
all_forcings = model.forcings_from_xarray(data.head(time=1))
print("all_forcings", all_forcings)

print("make forecast")
final_state, predictions = model.unroll(
    initial_state,
    all_forcings,
    steps=outer_steps,
    timedelta=timedelta,
    start_with_input=True,
)

print("final_state", final_state)
print("predictions", predictions)

print("predictions type:", type(predictions))
#print("predictions shape:", jax.tree_map(lambda x: x.shape, predictions))


predictions_ds = model.data_to_xarray(predictions, times=times)
#predictions_ds = model.data_to_xarray(predictions, times=None)

print("predictions_ds", predictions_ds)
#print("predictions_ds shape:", predictions_ds.shape)
print("predictions_ds time:", predictions_ds.time)


# create output_path if it doesn't exist
if not os.path.exists(output_path):
    os.makedirs(output_path)

# Save the model state
with open(f'{output_path}/model_state-{start_time}-{end_time}-{rng_key}.pkl', 'wb') as f:
    pickle.dump(final_state, f)

## fer el data to xarray amb "PREDICTIONS"

# Save the forecast
# final_step, predictions is a tuple of the advanced state at time steps * timestamp,
# and outputs with a leading time axis at the time-steps specified by steps, timedelta and start_with_input.

try:
    predictions_ds.to_netcdf(f"{output_path}/model_state-{start_time}-{end_time}-{rng_key}.nc")
except Exception as e:
    print("Error saving to netcdf:", e)
    # If the above fails, try saving as zarr
    print("Trying to save as zarr")

try:
    predictions_ds.to_zarr(f"{output_path}/model_state-{start_time}-{end_time}-{rng_key}.zarr", mode="w")
except Exception as e:
    print("Error saving to zarr:", e)




#predictions.to_zarr("forecast.zarr", mode="w")

# Visualize ERA5 vs NeuralGCM trajectories
# combined_ds.specific_humidity.sel(level=850).plot(
#    x='longitude', y='latitude', row='time', col='model', robust=True, aspect=2, size=2
