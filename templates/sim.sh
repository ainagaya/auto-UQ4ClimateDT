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
AI_CHECKPOINT=%MODEL.CHECKPOINT%
INPUT_TYPE=%MODEL.ICS%

INI_DATA_PATH=%GENERAL.INI_DATA_PATH%

MEMBER=%MEMBER%
RUN_DAYS=%RUN_DAYS%

YYYY=${START_DATE:0:4}

# Request keys
CLASS=%REQUEST.CLASS%
DATASET=%REQUEST.DATASET%
ACTIVITY=%REQUEST.ACTIVITY%
EXPERIMENT=%REQUEST.EXPERIMENT%
GENERATION=%REQUEST.GENERATION%
MODEL=%REQUEST.MODEL%
REALIZATION=%REQUEST.REALIZATION%
RESOLUTION=%REQUEST.RESOLUTION%
EXPVER=%REQUEST.EXPVER%
TYPE=%REQUEST.TYPE%
STREAM=%REQUEST.STREAM%

MEMBER=%MEMBER%
HPCROOTDIR=%HPCROOTDIR%

TIME1=%CHUNK_START_HOUR%
DELAY=%MODEL.DELAY%
TIME2=$(( TIME1 + DELAY ))

TIME1=${TIME1}00
TIME2=${TIME2}00

TIME="${TIME1}/${TIME2}"

# keep only the 8 first characters of the date
START_DATE=${START_DATE:0:8}
END_DATE=${END_DATE:0:8}

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

# coma oberta?
perturb_ics() {
    param="$1"
    member="$2"
    python3 "${HPCROOTDIR}/runscripts/perturb_var.py" \
        --input "${INPDIR}/${ACTIVITY}_${EXPERIMENT}_${YYYY}/aifs-climate-dt-${ACTIVITY}-${EXPERIMENT}-${START_DATE}-${TIME1}-${TIME2}.grib1" \
        --output "${INPDIR}/${ACTIVITY}_${EXPERIMENT}_${YYYY}/${MEMBER}/aifs-climate-dt-${ACTIVITY}-${EXPERIMENT}-${START_DATE}-${TIME1}-${TIME2}.grib1" \
        --shortname ${param} \
        --seed ${member}
}

conda_init
#conda activate ai-models
conda activate /gpfs/projects/bsc32/ml_models/emulator_models/ecmwf_ai_models/wf_emulator_snake_2
#conda activate /gpfs/scratch/bsc32/bsc032376/climate-emulators/env/wf_emulator_snake_2
module use /gpfs/projects/bsc32/software/rhel/9.2/modules/all
module load CDO
mkdir -p $OUTDIR/${MEMBER}
cd $OUTDIR/${MEMBER}

TARGETGRID=N320

if [ ${AI_MODEL,,} == "aifs" ]; then
    AI_MODEL_RUN="anemoi"
else
    AI_MODEL_RUN=${AI_MODEL}
fi


#perturb_ics "t" "${MEMBER}"

LEAD_TIME=$(( $RUN_DAYS * 24 ))

if [ ${INPUT_TYPE,,} == "fdb" ]; then
    ai-models --debug --input file --output file \
    --file ${INPDIR}/${ACTIVITY}_${EXPERIMENT}_${YYYY}/${MEMBER}/aifs-climate-dt-${ACTIVITY}-${EXPERIMENT}-${START_DATE}-${TIME1}-${TIME2}.grib1 \
    --path ${OUTDIR}/${MEMBER}/${AI_MODEL}-${START_DATE:0:8}-${START_TIME}.grib --time 0600 \
    --lead-time ${LEAD_TIME} anemoi --checkpoint ${AI_CHECKPOINT}
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
