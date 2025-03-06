import gcsfs
import jax
import numpy as np
import pickle
import xarray
import argparse
import yaml

from dinosaur import horizontal_interpolation
from dinosaur import spherical_harmonic
from dinosaur import xarray_utils
import neuralgcm


def parse_arguments():
    parser = argparse.ArgumentParser(description='Run NeuralGCM model')
    parser.add_argument('--config', '-c', type=str, default='config_neuralgcm.yaml',
                        help='Path to the config file')
    return parser.parse_args()

def read_config(config_path):
    with open(config_path, 'r') as f:
        return yaml.safe_load(f)
    
def define_variables(config):
    model_checkpoint = config['model_checkpoint']
    era5_path = config['era5_path']
    start_time = config['start_time']
    end_time = config['end_time']
    data_inner_steps = config['data_inner_steps']
    inner_steps = config['inner_steps']
    rng_key = config['rng_key']
    output_path = config['output_path']
    return model_checkpoint, era5_path, start_time, end_time, data_inner_steps, inner_steps, rng_key, output_path