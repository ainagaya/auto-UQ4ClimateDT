import gcsfs
import jax
import numpy as np
import pickle
import xarray

from dinosaur import horizontal_interpolation
from dinosaur import spherical_harmonic
from dinosaur import xarray_utils
import neuralgcm
import os

import argparse
import yaml


def parse_arguments():
    parser = argparse.ArgumentParser(description='Run NeuralGCM model')
    parser.add_argument('--config', '-c', type=str, default='config_neuralgcm.yaml',
                        help='Path to the config file')
    return parser.parse_args()

def read_config(config_path):
    with open(config_path, 'r') as f:
        return yaml.safe_load(f)

def validate_config(config):
    required_keys = ['model_checkpoint', 'era5_path', 'start_time', 'end_time', 'data_inner_steps', 'inner_steps']
    for key in required_keys:
        if key not in config:
            raise ValueError(f'Key {key} is missing from the config file')

def define_variables(config):
    model_checkpoint = config['model_checkpoint']
    era5_path = config['era5_path']
    start_time = config['start_time']
    end_time = config['end_time']
    data_inner_steps = config['data_inner_steps']
    inner_steps = config['inner_steps']
    rng_key = int(config['rng_key'])
    output_path = config['output_path']
    return model_checkpoint, era5_path, start_time, end_time, data_inner_steps, inner_steps, rng_key, output_path

args = parse_arguments()
config = read_config(args.config)
validate_config(config)
model_checkpoint, era5_path, start_time, end_time, data_inner_steps, inner_steps, rng_key, output_path = define_variables(config)

print("imported everything")

gcs = gcsfs.GCSFileSystem(token='anon')

print("gcs initialied")

with open(model_checkpoint, 'rb') as f:
  ckpt = pickle.load(f)

model = neuralgcm.PressureLevelModel.from_checkpoint(ckpt)

print("Defined model")

eval_era5 = xarray.open_zarr(era5_path, chunks=None)

outer_steps = 4 * 24 // inner_steps  # total of 4 days
timedelta = np.timedelta64(1, 'h') * inner_steps
times = (np.arange(outer_steps) * inner_steps)  # time axis in hours

print("initialize model state")

inputs = model.inputs_from_xarray(eval_era5.isel(time=0))
input_forcings = model.forcings_from_xarray(eval_era5.isel(time=0))
initial_state = model.encode(inputs, input_forcings, rng_key)

print("use persistence for forcing variables (SST and sea ice cover)")
all_forcings = model.forcings_from_xarray(eval_era5.head(time=1))

print("make forecast")
final_state, predictions = model.unroll(
    initial_state,
    all_forcings,
    steps=outer_steps,
    timedelta=timedelta,
    start_with_input=True,
)
predictions_ds = model.data_to_xarray(predictions, times=times)

# create output_path if it doesn't exist
if not os.path.exists(output_path):
    os.makedirs(output_path)

# Save the model state
with open(f'{output_path}/model_state-{start_time}-{end_time}-{rng_key}.pkl', 'wb') as f:
    pickle.dump(final_state, f)

# Selecting ERA5 targets from exactly the same time slice
target_trajectory = model.inputs_from_xarray(
    eval_era5
    .thin(time=(inner_steps // data_inner_steps))
    .isel(time=slice(outer_steps))
)
target_data_ds = model.data_to_xarray(target_trajectory, times=times)

## fer el data to xarray amb "PREDICTIONS"

combined_ds = xarray.concat([target_data_ds, predictions_ds], 'model')
combined_ds.coords['model'] = ['ERA5', 'NeuralGCM']

# Save the forecast
# final_step, predictions is a tuple of the advanced state at time steps * timestamp,
# and outputs with a leading time axis at the time-steps specified by steps, timedelta and start_with_input.

# what is final_state?
print(type(final_state))
print(dir(final_state))
print(final_state)

try:
    final_state.to_zarr("model_state.zarr", mode="w")
except:
    print("Error saving model state in Zarr")

try:
    final_state.to_netcdf("model_state.nc")
except:
    print("Error saving model state in NetCDF")

try:
    predictions_ds.to_zarr(f"{output_path}/model_state-{start_time}-{end_time}-{rng_key}.zarr", mode="w")
except:
    print("Error saving model state in Zarr")

try:
    predictions_ds.to_netcdf(f"{output_path}/model_state-{start_time}-{end_time}-{rng_key}.nc")
except:
    print("Error saving model state in NetCDF")

#predictions.to_zarr("forecast.zarr", mode="w")

# Visualize ERA5 vs NeuralGCM trajectories
# combined_ds.specific_humidity.sel(level=850).plot(
#    x='longitude', y='latitude', row='time', col='model', robust=True, aspect=2, size=2
#);
