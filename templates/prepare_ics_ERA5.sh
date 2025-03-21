#!/bin/bash

# PREPARE-ICS

HPCROOTDIR=%HPCROOTDIR%
START_DATE=%CHUNK_START_DATE%
TIME=%CHUNK_START_HOUR%
END_DATE=%CHUNK_END_DATE%

INPDIR=%DIRS.INPUT_DIR%

## AI-MODEL
MODEL_NAME=%MODEL.NAME%
AI_CHECKPOINT=%MODEL.CHECKPOINT%

## ERA5-PATH
INI_DATA_PATH=%DIRS.INI_DATA_PATH%

#####################################################
# Initializes conda
# Globals:
#
# Arguments:
#
#####################################################
function conda_init() {
    set +xuve
    # >>> conda initialize >>>
    # !! Contents within this block are managed by 'conda init' !!
    __conda_setup="$('/apps/GPP/ANACONDA/2023.07/bin/conda' 'shell.bash' 'hook' 2>/dev/null)"
    if [ $? -eq 0 ]; then
        eval "$__conda_setup"
    else
        if [ -f "/apps/GPP/ANACONDA/2023.07/etc/profile.d/conda.sh" ]; then
            . "/apps/GPP/ANACONDA/2023.07/etc/profile.d/conda.sh"
        else
            export PATH="/apps/GPP/ANACONDA/2023.07/bin:$PATH"
        fi
    fi
    unset __conda_setup
    set -xuve

}

conda_init
conda activate /gpfs/projects/bsc32/ml_models/emulator_models/ecmwf_ai_models/wf_emulator_snake_2
module use /gpfs/projects/bsc32/software/rhel/9.2/modules/all
module load CDO

file_format=grib

sfc_file="SFC_data_${AI_MODEL}_2023.${file_format}"
atm_file="ATM_data_${AI_MODEL}_2023.${file_format}"
if [ "${AI_MODEL}" == "aifs" ]; then
    atm_file="atm_${AI_MODEL}_6_12_2023.${file_format}"
    sfc_file="sfc_${AI_MODEL}_6_12_2023.${file_format}"
fi

path_to_sfc="${INI_DATA_PATH}/${sfc_file}"
path_to_atm="${INI_DATA_PATH}/${atm_file}"

tmp_file="${INPDIR}/${AI_MODEL}_${START_DATE}_${END_DATE}.${file_format}"

# List of dates between START_DATE and START_DATE + 1
dates=""
current_date=$START_DATE
while [ "$current_date" -le "$((START_DATE + 1))" ]; do
    dates="$dates/$current_date"
    current_date=$(date -d "$current_date + 1 day" +%Y%m%d)
done
dates=${dates#/}

mkdir -p $INPDIR

grib_copy -w date=${dates} $path_to_atm $INPDIR/"tmp_atm.grib"
grib_copy -w date=${dates} $path_to_sfc $INPDIR/"tmp_sfc.grib"
cat $INPDIR/"tmp_atm.grib" $INPDIR/"tmp_sfc.grib"  > $tmp_file
