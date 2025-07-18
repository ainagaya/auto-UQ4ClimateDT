#!/bin/bash

# postproc neuralgcm

HPCROOTDIR=%HPCROOTDIR%
EXPID=%DEFAULT.EXPID%
JOBNAME=%JOBNAME%

JOBNAME_WITHOUT_EXPID=$(echo ${JOBNAME} | sed 's/^[^_]*_//')

logs_dir=${HPCROOTDIR}/LOG_${EXPID}
configfile=$logs_dir/config_neuralgcm_${JOBNAME_WITHOUT_EXPID}

source ${HPCROOTDIR}/lib/MARENOSTRUM5/util.sh
conda_init
conda activate /gpfs/scratch/bsc32/bsc032376/envs/neuralgcm

python3 $HPCROOTDIR/runscripts/postproc_neuralgcm.py -c $configfile
