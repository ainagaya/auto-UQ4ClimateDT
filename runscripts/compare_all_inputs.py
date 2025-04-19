import xarray as xr
import matplotlib.pyplot as plt
import numpy as np
import os

# Load datasets
ds_init = xr.open_dataset("model_initial_conditions.nc")
ds_init_era = xr.open_dataset("model_initial_conditions_era.nc")
ds_forc = xr.open_dataset("model_forcings.nc")
ds_forc_era = xr.open_dataset("model_forcings_era.nc")

# Create output dir
os.makedirs("plots", exist_ok=True)

def compare_datasets(ds1, ds2, label1, label2):
    common_vars = set(ds1.data_vars).intersection(set(ds2.data_vars))
    for var in common_vars:
        print(f"\n🔍 Comparing variable: {var}")
        da1 = ds1[var]
        da2 = ds2[var]

        # Interpolate if grids are not aligned
        if not da1.latitude.equals(da2.latitude) or not da1.longitude.equals(da2.longitude):
            da2 = da2.interp(latitude=da1.latitude, longitude=da1.longitude, method="nearest")

        diff = da1 - da2
        with np.errstate(divide='ignore', invalid='ignore'):
            perc_diff = (abs(diff) / da2) * 100
            perc_diff = perc_diff.where(np.isfinite(perc_diff), 0)

        if "level" in diff.dims:
            for level in diff.level.values:
                diff_lvl = diff.sel(level=level)
                perc_lvl = perc_diff.sel(level=level)

                # Plot absolute difference
                plt.figure(figsize=(10, 4))
                if "latitude" in diff_lvl.dims and "longitude" in diff_lvl.dims:
                    diff_lvl.plot(cmap="RdBu", robust=True)
                else:
                    diff_lvl.plot()
                plt.title(f"{var} ABS diff ({label1} - {label2}) at level {level}")
                plt.tight_layout()
                plt.savefig(f"plots/diff_abs_{var}_{label1}_vs_{label2}_level_{int(level)}.png")
                plt.close()

                # Plot percentage difference
                plt.figure(figsize=(10, 4))
                if "latitude" in perc_lvl.dims and "longitude" in perc_lvl.dims:
                    perc_lvl.plot(cmap="coolwarm", robust=True)
                else:
                    perc_lvl.plot()
                plt.title(f"{var} % diff ({label1} vs {label2}) at level {level}")
                plt.tight_layout()
                plt.savefig(f"plots/diff_perc_{var}_{label1}_vs_{label2}_level_{int(level)}.png")
                plt.close()

                # Print stats
                print(f"  Level {level}")
                print(f"    Mean ABS diff: {diff_lvl.mean().item():.4f}")
                print(f"    Max  ABS diff: {diff_lvl.max().item():.4f}")
                print(f"    Mean %  diff: {perc_lvl.mean().item():.2f}%")
                print(f"    Max  %  diff: {perc_lvl.max().item():.2f}%")

        else:
            # No level dimension — just do one plot
            plt.figure(figsize=(10, 4))
            if "latitude" in diff.dims and "longitude" in diff.dims:
                diff.plot(cmap="RdBu", robust=True)
            else:
                diff.plot()
            plt.title(f"{var} ABS diff ({label1} - {label2})")
            plt.tight_layout()
            plt.savefig(f"plots/diff_abs_{var}_{label1}_vs_{label2}.png")
            plt.close()

            plt.figure(figsize=(10, 4))
            if "latitude" in perc_diff.dims and "longitude" in perc_diff.dims:
                perc_diff.plot(cmap="coolwarm", robust=True)
            else:
                perc_diff.plot()
            plt.title(f"{var} % diff ({label1} vs {label2})")
            plt.tight_layout()
            plt.savefig(f"plots/diff_perc_{var}_{label1}_vs_{label2}.png")
            plt.close()

            # Print stats
            print(f"  Mean ABS diff: {diff.mean().item():.4f}")
            print(f"  Max  ABS diff: {diff.max().item():.4f}")
            print(f"  Mean %  diff: {perc_diff.mean().item():.2f}%")
            print(f"  Max  %  diff: {perc_diff.max().item():.2f}%")



# Run comparisons
print("\n🧊 Comparing Initial Conditions...")
compare_datasets(ds_init, ds_init_era, "model", "era")

print("\n🔥 Comparing Forcings...")
compare_datasets(ds_forc, ds_forc_era, "model", "era")
