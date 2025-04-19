### From two ICS datasets in zarr, take the selected variables from the second and copy them to the third (a copy of the fist)
### and save the result in a third directory

import os
import xarray as xr
import numpy as np
import argparse
import pandas as pd
import zarr


def parse_args():
    parser = argparse.ArgumentParser(description="Copy variables from one ICS to another")
    parser.add_argument(
        "--icsdir1",
        type=str,
        required=True,
        help="Path to the first ICS directory",
    )
    parser.add_argument(
        "--icsdir2",
        type=str,
        required=True,
        help="Path to the second ICS directory",
    )
    parser.add_argument(
        "--icsdirnew",
        type=str,
        required=True,
        help="Path to the new ICS directory",
    )
    return parser.parse_args()

def copy_variables(icsdir1, icsdir2, variables, output_dir):
    # Open the first ICS directory
    ics1 = xr.open_zarr(icsdir1, mode="r")
    # Open the second ICS directory
    ics2 = xr.open_zarr(icsdir2, mode="r")

    # Create a copy of the first ICS directory in memory
    ics3 = ics1.copy(deep=True)

    # Loop over the variables and copy them from icsdir2 to ics3
    for var in variables:
        if var in ics2:
            ics3[var] = ics2[var]
            print(f"Copied variable {var} from {icsdir2} to the output dataset")
        else:
            print(f"Variable {var} not found in {icsdir2}")

    # Save the modified dataset to the output directory
    os.makedirs(output_dir, exist_ok=True)
    ics3.to_zarr(output_dir, mode="w")
    print(f"Saved the modified dataset to {output_dir}")

def main():
    args = parse_args()
    icsdir1 = args.icsdir1
    icsdir2 = args.icsdir2

    list_of_variables = ["temperature", "sea_ice_cover", "u_component_of_wind", "v_component_of_wind", "specific_humidity", "specific_cloud_ice_water_content",
                        "geopotential", "specific_cloud_liquid_water_content", "sea_surface_temperature" ]

    # We will repeat the process for each variable in the list
    # the directory will be called "output_dir" + "_" + fdb_var_$variable

    for variable in list_of_variables:
        output_dir = f"{args.icsdirnew}/fdb_var_{variable}"
        copy_variables(args.icsdir1, args.icsdir2, [variable], output_dir)

if __name__ == "__main__":
    main()
