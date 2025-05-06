def rename_variables(data, translator_file=None):
    data_copy = data.copy()
    for var in data_copy.variables:
        if "standard_name" in data_copy[var].attrs:
            original_name = var
            standard_name = data_copy[var].attrs["standard_name"]
            renamed_name = standard_name if standard_name != "unknown" else original_name
            data_copy = data_copy.rename({var: renamed_name})

            if translator_file and renamed_name in translator_file:
                translated_name = translator_file[renamed_name]
                data_copy = data_copy.rename({renamed_name: translated_name})
    return data_copy

def fix_sst(data):
    if "sea_surface_temperature" in data.variables:
        sst = data["sea_surface_temperature"]
        sst.attrs["units"] = "K"
        sst.values +
