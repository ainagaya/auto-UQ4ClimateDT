#!/bin/bash

# PREPARE-ICS

HPCROOTDIR=%HPCROOTDIR%
START_DATE=%CHUNK_START_DATE%
TIME=%CHUNK_START_HOUR%
END_DATE=%CHUNK_END_DATE%

## AI-MODEL
MODEL_NAME=%MODEL.NAME%
AI_CHECKPOINT=%MODEL.CHECKPOINT_NAME%

## ERA5-PATH
ERA5_PATH=%DIRS.ERA5_PATH%

JOBNAME=%JOBNAME%
EXPID=%DEFAULT.EXPID%

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
conda activate neuralgcm

JOBNAME_WITHOUT_EXPID=$(echo ${JOBNAME} | sed 's/^[^_]*_//')

logs_dir=${HPCROOTDIR}/LOG_${EXPID}
configfile=$logs_dir/config_neuralgcm_${JOBNAME_WITHOUT_EXPID}

# Check if the ICs already exist or not for this
# specific chunk. If they do, we skip the preparation
# of the ICs. If they don't, we prepare them.
ICs_path=${ERA5_PATH}/${MODEL_NAME}/${AI_CHECKPOINT}/${START_DATE}-${END_DATE}
if [ -d ${ICs_path} ]; then
    echo "ICs already exist for this chunk. Skipping."
else
    mkdir -p ${ICs_path}
    python3 $HPCROOTDIR/lib/download_era5.py --config $configfile
fi
