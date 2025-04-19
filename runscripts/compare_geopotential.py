import xarray as xr
import matplotlib.pyplot as plt
import os

# Setup
file_model = "model_initial_conditions.nc"
file_era = "model_initial_conditions_era.nc"
varname = "geopotential"  # adjust if different
out_dir = "plots_geopotential"
os.makedirs(out_dir, exist_ok=True)

# Load data
ds_model = xr.open_dataset(file_model)
ds_era = xr.open_dataset(file_era)

# Check geopotential exists
if varname not in ds_model or varname not in ds_era:
    raise ValueError(f"'{varname}' not found in both datasets!")

da_model = ds_model[varname]
da_era = ds_era[varname]

# 📏 Metadata comparison
print("\n📋 Metadata Comparison:")
print("Model Units:", da_model.attrs.get("units", "None"))
print("ERA   Units:", da_era.attrs.get("units", "None"))
print("Model Attrs:", da_model.attrs)
print("ERA   Attrs:", da_era.attrs)

# Interpolate if needed
if not da_model.latitude.equals(da_era.latitude) or not da_model.longitude.equals(da_era.longitude):
    da_era = da_era.interp(latitude=da_model.latitude, longitude=da_model.longitude, method="nearest")

# 🗺️ Plot for each level
if "level" not in da_model.dims:
    raise ValueError("No 'level' dimension found in geopotential data!")

for level in da_model.level.values:
    z_model = da_model.sel(level=level)
    z_era = da_era.sel(level=level)
    z_diff = z_era - z_model

    fig, axs = plt.subplots(1, 3, figsize=(18, 5))

    z_model.plot(ax=axs[0], cmap="viridis", robust=True)
    axs[0].set_title(f"Model Geopotential @ {level} hPa")

    z_era.plot(ax=axs[1], cmap="viridis", robust=True)
    axs[1].set_title(f"ERA Geopotential @ {level} hPa")

    z_diff.plot(ax=axs[2], cmap="RdBu", robust=True)
    axs[2].set_title(f"ERA - Model Diff @ {level} hPa")

    for ax in axs:
        ax.set_xlabel("Longitude")
        ax.set_ylabel("Latitude")

    plt.tight_layout()
    plt.savefig(f"{out_dir}/geopotential_comparison_level_{int(level)}.png")
    plt.close()

    # Print stats
    print(f"\n📊 Level {level} hPa:")
    print(f"  ERA  mean: {z_era.mean().item():.2f}")
    print(f"  Model mean: {z_model.mean().item():.2f}")
    print(f"  Mean diff: {(z_era - z_model).mean().item():.2f}")
    print(f"  Max  diff: {(z_era - z_model).max().item():.2f}")
