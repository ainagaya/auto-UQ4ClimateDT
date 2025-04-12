import gcsfs
import jax
import numpy as np
import pickle
import xarray

from dinosaur import horizontal_interpolation
from dinosaur import spherical_harmonic
from dinosaur import xarray_utils
import neuralgcm

from functions import parse_arguments, read_config

def define_variables(config):
    model_checkpoint = config['model_checkpoint']
    INI_DATA_PATH = config['INI_DATA_PATH']
    start_time = config['start_time']
    end_time = start_time
    data_inner_steps = config['data_inner_steps']
    inner_steps = config['inner_steps']
    output_path = config['output_path']
    return model_checkpoint, INI_DATA_PATH, start_time, end_time, data_inner_steps, inner_steps, output_path


args = parse_arguments()
config = read_config(args.config)

gcs = gcsfs.GCSFileSystem(token='anon')

print("gcs initialied")

model_checkpoint, INI_DATA_PATH, start_time, end_time, data_inner_steps, inner_steps, output_path = define_variables(config)

with open(f'{model_checkpoint}', 'rb') as f:
  ckpt = pickle.load(f)

model = neuralgcm.PressureLevelModel.from_checkpoint(ckpt)

INI_DATA_PATH_remote = 'gs://gcp-public-data-arco-era5/ar/full_37-1h-0p25deg-chunk-1.zarr-v3'
full_era5 = xarray.open_zarr(gcs.get_mapper(INI_DATA_PATH_remote), chunks=None)

## M'ho puc baixar

sliced_era5 = (
    full_era5
    [model.input_variables + model.forcing_variables]
    .pipe(
        xarray_utils.selective_temporal_shift,
        variables=model.forcing_variables,
        time_shift='24 hours',
    )
    .sel(time=slice(start_time, end_time, data_inner_steps))
    .compute()
)

era5_grid = spherical_harmonic.Grid(
    latitude_nodes=full_era5.sizes['latitude'],
    longitude_nodes=full_era5.sizes['longitude'],
    latitude_spacing=xarray_utils.infer_latitude_spacing(full_era5.latitude),
    longitude_offset=xarray_utils.infer_longitude_offset(full_era5.longitude),
)
regridder = horizontal_interpolation.ConservativeRegridder(
    era5_grid, model.data_coords.horizontal, skipna=True
)
eval_era5 = xarray_utils.regrid(sliced_era5, regridder)
eval_era5 = xarray_utils.fill_nan_with_nearest(eval_era5)

# save data to local disk in zarr
eval_era5.to_zarr(f"{INI_DATA_PATH}", mode='w')
