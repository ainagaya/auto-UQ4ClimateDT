#!/bin/bash

# SIM

DATE=%CHUNK_START_DATE%
TIME=%CHUNK_START_HOUR%
INPDIR=%DIRS.INPUT_DIR%
OUTDIR=%DIRS.OUTPUT_DIR%

# Request keys
LEVTYPE=%REQUEST.LEVTYPE%

AI_MODEL=%AI_MODEL%

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
conda activate ai-models

mkdir -p $OUTDIR
cd $OUTDIR

ai-models --file ${INPDIR}/${AI_MODEL}_${LEVTYPE}_tp_${DATE}_${TIME}.grib --path ${OUTDIR}/${AI_MODEL}-${DATE}-${TIME}.grib ${AI_MODEL}
