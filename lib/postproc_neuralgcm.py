import xarray as xr
import matplotlib.pyplot as plt
import glob
import os

from functions import parse_arguments, read_config

def define_variables(config):
    model_checkpoint = config['model_checkpoint']
    era5_path = config['era5_path']
    start_time = config['start_time']
    end_time = config['end_time']
    data_inner_steps = config['data_inner_steps']
    inner_steps = config['inner_steps']
    plots_path = config['plots_path']
    members = config['members']
    output_path = config['output_path']
    return model_checkpoint, era5_path, start_time, end_time, data_inner_steps, inner_steps, plots_path, members, output_path
args = parse_arguments()
config = read_config(args.config)
model_checkpoint, era5_path, start_time, end_time, data_inner_steps, inner_steps, plots_path, members, output_path = define_variables(config)

# Define folders containing the NetCDF files
members = list(members)  # List of folder names
# directories will be output_dir/members[i]/
folders = [os.path.join(output_path, member) for member in members]

# Define file pattern inside each folder
file_pattern = f"model_state-{start_time}-{end_time}-*.nc"  # Adjust as needed

# Define selected level
selected_level = 1  # Use level 1 for all variables

os.makedirs(plots_path, exist_ok=True)  # Create directory if it doesn't exist

# Collect all unique variable names from all files
variables = set()
for folder in folders:
    file_list = sorted(glob.glob(os.path.join(folder, file_pattern)))
    if file_list:
        ds = xr.open_dataset(file_list[0])  # Open the first file in the folder
        variables.update(ds.data_vars.keys())  # Add all variable names

# Process each variable
for var_name in sorted(variables):
    plt.figure(figsize=(10, 5))  # Create a new figure for each variable

    for folder in folders:
        folder_label = os.path.basename(folder)  # Extracts folder name (e.g., "1", "2", "3")
        file_list = sorted(glob.glob(os.path.join(folder, file_pattern)))  # Get all matching files

        if not file_list:
            print(f"No files found in {folder}/")
            continue  # Skip this folder if no files are found

        for file_path in file_list:
            # Load dataset
            ds = xr.open_dataset(file_path)

            # Check if the variable exists in this dataset
            if var_name not in ds:
                print(f"Skipping {var_name} in {folder}: Variable not found.")
                continue  # Skip this variable if it's missing

            var = ds[var_name]  # Select variable

            # Ensure level exists before selecting
            if "level" in var.dims:
                var_at_level = var.sel(level=selected_level)
            else:
                print(f"Skipping {var_name} in {folder}: No 'level' dimension.")
                continue  # Skip this variable if it doesn't have a level dimension

            # Compute spatial average (assuming lat/lon are spatial dimensions)
            var_mean = var_at_level.mean(dim=["latitude", "longitude"])

            # Plot time series
            var_mean.plot(linestyle="-", marker="o", label=f"Run {folder_label}")

    # Final plot settings
    plt.xlabel("Time")
    plt.ylabel(var.attrs.get("units", "Unknown"))
    plt.title(f"Time Evolution of {var_name} at Level {selected_level}")
    plt.legend()
    plt.grid()

    # Save the plot
    plot_filename = f"{plots_path}/{var_name}.png"
    plt.savefig(plot_filename, dpi=300)
    plt.close()  # Close the figure to free memory

    print(f"Saved plot: {plot_filename}")
