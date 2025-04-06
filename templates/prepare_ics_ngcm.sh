#!/bin/bash

# Input variables (should be passed via env or set before calling the script)
HPCROOTDIR=%HPCROOTDIR%
CHUNK_START_DATE=%CHUNK_START_DATE%
CHUNK_END_DATE=%CHUNK_END_DATE%

MODEL_NAME=%MODEL.NAME%
MODEL_CHECKPOINT_NAME=%MODEL.CHECKPOINT_NAME%
INI_DATA_PATH=%DIRS.INI_DATA_PATH%
DATA_PATH="${INI_DATA_PATH}/${MODEL_NAME}/${MODEL_CHECKPOINT_NAME}/${CHUNK_START_DATE}-${CHUNK_END_DATE}"

REGENERATE_ICS=%MODEL.REGENERATE_ICS%
IC_SOURCE=%MODEL.IC_SOURCE%  # "ERA5" or "FDB"

JOBNAME=%JOBNAME%
EXPID=%DEFAULT.EXPID%
GSV_CONTAINER=%GSV.CONTAINER%

FDB_HOME=/gpfs/projects/ehpc01/dte/fdb
SIF_PATH=/gpfs/scratch/ehpc204/bsc032376/neuralgcm_bsc_v1.0.sif

# Derived paths
JOBNAME_WITHOUT_EXPID=$(echo ${JOBNAME} | sed 's/^[^_]*_//')
LOGS_DIR=${HPCROOTDIR}/LOG_${EXPID}
CONFIGFILE=$LOGS_DIR/config_neuralgcm_${JOBNAME_WITHOUT_EXPID}
REQUESTS_DIR=${HPCROOTDIR}/requests

# Load Singularity module
ml singularity

source ${LIBDIR}/functions.sh
create_ics=$(check_existing_ics $DATA_PATH $REGENERATE_ICS)

if [ "$create_ics" = "false" ]; then
    echo "ICs already exist for this chunk at $DATA_PATH. Skipping."
else
    if [ "$IC_SOURCE" = "FDB" ]; then
        prepare_ics_fdb $HPCROOTDIR $FDB_HOME $REQUESTS_DIR $CHUNK_START_DATE $CHUNK_END_DATE $DATA_PATH $GSV_CONTAINER
    elif [ "$IC_SOURCE" = "ERA5" ]; then
        prepare_ics_era5 $HPCROOTDIR $LOGS_DIR $CONFIGFILE $SIF_PATH
    fi
fi


