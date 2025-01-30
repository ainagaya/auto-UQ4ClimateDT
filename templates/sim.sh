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

AI_MODEL=%AI_MODEL%
AI_CHECKPOINT=%AI_CHECKPOINT%
INPUT_TYPE=%INPUT_TYPE%

ERA5_PATH=%GENERAL.ERA5_PATH%

MEMBER=%MEMBER%
RUN_DAYS=%RUN_DAYS%

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
mkdir -p $OUTDIR
cd $OUTDIR

TARGETNGRID=320

if [ ${AI_MODEL,,} == "aifs" ]; then
    AI_MODEL_RUN="anemoi"
else
    AI_MODEL_RUN=${AI_MODEL}
fi

LEAD_TIME=$(( $RUN_DAYS * 24 ))

if [ ${INPUT_TYPE,,} == "fdb" ]; then
    ai-models --debug --input file --output file \
    --file ${INPDIR}/${AI_MODEL}_${START_DATE:0:8}_${START_TIME}_N${TARGETNGRID}.grib \
    --path ${OUTDIR}/${AI_MODEL}-${START_DATE:0:8}-${START_TIME}.grib --time 0600 \
    --lead-time ${LEAD_TIME} ${AI_MODEL} --checkpoint ${AI_CHECKPOINT}
elif [ ${INPUT_TYPE,,} == "era5_grib" ]; then
    file_format=grib
    ai-models --input file --file "${INPDIR}/${AI_MODEL}_${START_DATE}_${END_DATE}.${file_format}" \
    --output file --path ${OUTDIR}/${AI_MODEL}-${START_DATE}_${END_DATE}_${MEMBER}.grib \
    --lead_time ${LEAD_TIME} --date ${START_DATE} --time ${START_TIME} \
    ${AI_MODEL_RUN} --checkpoint ${AI_CHECKPOINT}
else
    export PATH=/gpfs/projects/ehpc01/dte/bin:$PATH
    ai-models --input cds --date ${START_DATE} --time ${TIME} ${AI_MODEL} --checkpoint ${AI_CHECKPOINT}
fi

#ai-models --input file --file /gpfs/projects/bsc32/ml_models/emulator_models/aifs/inference_files/example-input-aifs021.grib \
# --output file --time 0600 --date 20240808 --path test_output.grib --lead-time 360 anemoi \
# --checkpoint /gpfs/projects/bsc32/ml_models/emulator_models/aifs/inference_files/inference-aifs-0.2.1-anemoi.ckpt