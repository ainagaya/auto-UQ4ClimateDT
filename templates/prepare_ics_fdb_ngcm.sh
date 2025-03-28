#!/bin/bash

HPCROOTDIR=%HPCROOTDIR%

FDB_HOME=/gpfs/projects/ehpc01/dte/fdb
DATA_PATH="%DIRS.INI_DATA_PATH%/%MODEL.NAME%/%MODEL.CHECKPOINT_NAME%/%CHUNK_START_DATE%-%CHUNK_END_DATE%"
PROJE=/gpfs/projects/ehpc01
REGENERATE_ICS=%MODEL.REGENERATE_ICS%

GSV_CONTAINER=%GSV.CONTAINER%

# if we want to regenerate the ICS, remove the data_path directory
if [ "${REGENERATE_ICS,,}" = "true" ]; then
    rm -rf ${DATA_PATH}
fi


mkdir -p $DATA_PATH
mkdir -p ${HPCROOTDIR}/requests

# generate the requests
python3 ${HPCROOTDIR}/runscripts/build_requests.py --general ${HPCROOTDIR}/runscripts/general_request.yaml --model ${HPCROOTDIR}/runscripts/neuralgcm.yaml --output ${HPCROOTDIR}/requests

ml singularity

singularity exec --env FDB_HOME=$FDB_HOME --env HPCROOTDIR=$HPCROOTDIR \
    --bind $FDB_HOME,$DATA_PATH,$HPCROOTDIR/runscripts,$HPCROOTDIR/requests,$PWD ${GSV_CONTAINER} \
    bash -c "python3 ${HPCROOTDIR}/runscripts/retrieve.py --requests ${HPCROOTDIR}/requests \
    --output $DATA_PATH --translator ${HPCROOTDIR}/runscripts/translation-ngcm.yaml"
