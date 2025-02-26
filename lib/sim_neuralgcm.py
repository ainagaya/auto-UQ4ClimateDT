import gcsfs
import jax
import numpy as np
import pickle
import xarray

from dinosaur import horizontal_interpolation
from dinosaur import spherical_harmonic
from dinosaur import xarray_utils
import neuralgcm

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
    return model_checkpoint, era5_path, start_time, end_time, data_inner_steps, inner_steps

args = parse_arguments()
config = read_config(args.config)
validate_config(config)
model_checkpoint, era5_path, start_time, end_time, data_inner_steps, inner_steps = define_variables(config)

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
rng_key = jax.random.key(42)  # optional for deterministic models
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

# Save the model state
with open('model_state.pkl', 'wb') as f:
    pickle.dump(final_state, f)

# Selecting ERA5 targets from exactly the same time slice
target_trajectory = model.inputs_from_xarray(
    eval_era5
    .thin(time=(inner_steps // data_inner_steps))
    .isel(time=slice(outer_steps))
)
target_data_ds = model.data_to_xarray(target_trajectory, times=times)

combined_ds = xarray.concat([target_data_ds, predictions_ds], 'model')
combined_ds.coords['model'] = ['ERA5', 'NeuralGCM']

# Save the forecast
combined_ds.to_zarr('forecast.zarr')

# Visualize ERA5 vs NeuralGCM trajectories
combined_ds.specific_humidity.sel(level=850).plot(
    x='longitude', y='latitude', row='time', col='model', robust=True, aspect=2, size=2
);
