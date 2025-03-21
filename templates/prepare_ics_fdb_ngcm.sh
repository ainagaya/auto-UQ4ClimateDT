#!/bin/bash

HPCROOTDIR=%HPCROOTDIR%

FDB_HOME=/gpfs/projects/ehpc01/dte/fdb
DATA_PATH=${HPCROOTDIR}/data
PROJE=/gpfs/projects/ehpc01

# generate the requests
python3 ${HPCROOTDIR}/runscripts/build_requests.py --general ${HPCROOTDIR}/runscripts/general_request.yaml --model ${HPCROOTDIR}/runscripts/neuralgcm.yaml --output ${HPCROOTDIR}/requests

ml singularity

singularity exec --env FDB_HOME=$FDB_HOME --bind $FDB_HOME,$DATA_PATH,$PWD $PROJE/containers/gsv/gsv_v2.6.0.sif bash -c "python3 retrieve.py --requests ${HPCROOTDIR}/requests --output $DATA_PATH"
