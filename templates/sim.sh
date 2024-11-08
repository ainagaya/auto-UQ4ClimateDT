#!/bin/bash

# SIM

DATE=%CHUNK_START_DATE%
TIME=%CHUNK_START_HOUR%
INPDIR=%DIRS.INPUT_DIR%
OUTDIR=%DIRS.OUTPUT_DIR%

# Request keys
LEVTYPE=%REQUEST.LEVTYPE%

AI_MODEL=%AI_MODEL%
AI_CHECKPOINT=%AI_CHECKPOINT%

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


mkdir -p $OUTDIR
cd $OUTDIR

#ai-models --debug --input file --output file \
#--file ${INPDIR}/${AI_MODEL}_${LEVTYPE}_tp_${DATE}_${TIME}.grib \
#--path ${OUTDIR}/${AI_MODEL}-${DATE}-${TIME}.grib --time 0600 \
#--lead-time 360 ${AI_MODEL} --checkpoint ${AI_CHECKPOINT}

ai-models --input file --file /gpfs/projects/bsc32/ml_models/emulator_models/aifs/inference_files/example-input-aifs021.grib \
 --output file --time 0600 --date 20240808 --path test_output.grib --lead-time 360 anemoi \
 --checkpoint /gpfs/projects/bsc32/ml_models/emulator_models/aifs/inference_files/inference-aifs-0.2.1-anemoi.ckpt