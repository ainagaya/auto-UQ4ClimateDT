#!/bin/bash

HPCROOTDIR=%HPCROOTDIR%

FDB_HOME=/gpfs/projects/ehpc01/dte/fdb
DATA_PATH="%DIRS.INI_DATA_PATH%/%MODEL.NAME%/%MODEL.CHECKPOINT_NAME%/%CHUNK_START_DATE%-%CHUNK_END_DATE%"
PROJE=/gpfs/projects/ehpc01

mkdir -p $DATA_PATH
mkdir -p ${HPCROOTDIR}/requests

# generate the requests
python3 ${HPCROOTDIR}/runscripts/build_requests.py --general ${HPCROOTDIR}/runscripts/general_request.yaml --model ${HPCROOTDIR}/runscripts/neuralgcm.yaml --output ${HPCROOTDIR}/requests

ml singularity

singularity exec --env FDB_HOME=$FDB_HOME --env HPCROOTDIR=$HPCROOTDIR --bind $FDB_HOME,$DATA_PATH,$HPCROOTDIR/runscripts,$HPCROOTDIR/requests,$PWD $PROJE/containers/gsv/gsv_v2.6.0.sif bash -c "python3 ${HPCROOTDIR}/runscripts/retrieve.py --requests ${HPCROOTDIR}/requests --output $DATA_PATH"
