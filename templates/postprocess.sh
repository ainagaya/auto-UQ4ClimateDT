#!/bin/bash

# SIM

START_DATE=%CHUNK_START_DATE%
START_TIME=%CHUNK_START_HOUR%
END_DATE=%CHUNK_END_DATE%
END_TIME=%CHUNK_END_HOUR%

INPDIR=%DIRS.INPUT_DIR%
OUTDIR=%DIRS.OUTPUT_DIR%

# Request keys
LEVTYPE=%REQUEST.LEVTYPE%

AI_MODEL=%MODEL.NAME%
AI_CHECKPOINT=%MODEL.CHECKPOINT%
INPUT_TYPE=%MODEL.ICS%

INI_DATA_PATH=%GENERAL.INI_DATA_PATH%
MEMBER=%MEMBER%
PERIOD=%POSTPROCESS.PERIOD%

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
#conda activate ai-models
conda activate /gpfs/projects/bsc32/ml_models/emulator_models/ecmwf_ai_models/wf_emulator_snake_2
#conda activate /gpfs/scratch/bsc32/bsc032376/climate-emulators/env/wf_emulator_snake_2
module use /gpfs/projects/bsc32/software/rhel/9.2/modules/all
module load CDO
module load NCO

cd $OUTDIR

# Create surrogate series, taking day $PERIOD of each simulation
grib_copy -w stepRange=${PERIOD} $OUTDIR/${AI_MODEL}-${START_DATE}_${END_DATE}_${MEMBER}.grib $OUTDIR/${AI_MODEL}-${START_DATE}_${END_DATE}_${MEMBER}_surrogate.grib

# Concatenate all surrogates
touch $OUTDIR/${AI_MODEL}-${START_DATE}_${MEMBER}_surrogate_all.grib
cat $OUTDIR/${AI_MODEL}-${START_DATE}_${END_DATE}_${MEMBER}_surrogate.grib >> $OUTDIR/surrogate_series/${AI_MODEL}-${START_DATE}_${MEMBER}_surrogate_all.grib

rm $OUTDIR/${AI_MODEL}-${START_DATE}_${END_DATE}_${MEMBER}_surrogate.grib
