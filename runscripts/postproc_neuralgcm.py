import xarray as xr
import plotly.graph_objects as go
import glob
import os

from functions import parse_arguments, read_config

def define_variables(config):
    model_checkpoint = config['model_checkpoint']
    INI_DATA_PATH = config['INI_DATA_PATH']
    start_time = config['start_time']
    end_time = config['end_time']
    data_inner_steps = config['data_inner_steps']
    inner_steps = config['inner_steps']
    plots_path = config['plots_path']
    members = config['members']
    output_path = config['output_path']
    return model_checkpoint, INI_DATA_PATH, start_time, end_time, data_inner_steps, inner_steps, plots_path, members, output_path

args = parse_arguments()
config = read_config(args.config)
model_checkpoint, INI_DATA_PATH, start_time, end_time, data_inner_steps, inner_steps, plots_path, members, output_path = define_variables(config)


# We have to go one directory up to get the correct path
output_path = os.path.abspath(os.path.join(output_path, os.pardir))

members = list(members)
folders = [os.path.join(output_path, member) for member in members]

file_pattern = f"model_state-{start_time}-{end_time}-*.nc"
selected_level = 1

os.makedirs(plots_path, exist_ok=True)

# Collect all unique variable names
variables = set()
for folder in folders:
    file_list = sorted(glob.glob(os.path.join(folder, file_pattern)))
    if file_list:
        ds = xr.open_dataset(file_list[0])
        variables.update(ds.data_vars.keys())

# Load original data
original_ds = xr.open_dataset(INI_DATA_PATH)

# Process each variable
for var_name in sorted(variables):
    fig = go.Figure()

    for folder in folders:
        folder_label = os.path.basename(folder)
        file_list = sorted(glob.glob(os.path.join(folder, file_pattern)))

        if not file_list:
            print(f"No files found in {folder}/")
            continue

        for file_path in file_list:
            ds = xr.open_dataset(file_path)

            if var_name not in ds:
                print(f"Skipping {var_name} in {folder}: Variable not found.")
                continue

            var = ds[var_name]

            if "level" in var.dims:
                var_at_level = var.sel(level=selected_level)
            else:
                print(f"Skipping {var_name} in {folder}: No 'level' dimension.")
                continue

            var_mean = var_at_level.mean(dim=["latitude", "longitude"])

            fig.add_trace(go.Scatter(
                x=var_mean['time'].values,
                y=var_mean.values,
                mode='lines+markers',
                name=f"Run {folder_label}",
                line=dict(width=2),
                marker=dict(size=4),
            ))

    # Add original model trajectory
    if var_name in original_ds:
        original_var = original_ds[var_name]
        if "level" in original_var.dims:
            original_at_level = original_var.sel(level=selected_level)
            original_mean = original_at_level.mean(dim=["latitude", "longitude"])

            fig.add_trace(go.Scatter(
                x=original_mean['time'].values,
                y=original_mean.values,
                mode='lines',
                name="Original Data",
                line=dict(color="black", width=3, dash="dash"),
            ))
        else:
            print(f"Skipping original {var_name}: No 'level' dimension.")
    else:
        print(f"Original data missing variable: {var_name}")

    # Final plot settings
    fig.update_layout(
        title=f"Time Evolution of {var_name} at Level {selected_level}",
        xaxis_title="Time",
        yaxis_title=original_ds[var_name].attrs.get("units", "Unknown") if var_name in original_ds else "Unknown",
        legend=dict(title="Legend"),
        template="plotly_white",
        width=1000,
        height=600,
    )

    # Save plot
    plot_filename = f"{plots_path}/{var_name}.html"
    fig.write_html(plot_filename)
    print(f"Saved plot: {plot_filename}")
