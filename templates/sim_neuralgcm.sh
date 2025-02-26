#!/bin/bash

# SIM neuralgcm

HPCROOTDIR=%HPCROOTDIR%
EXPID=%DEFAULT.EXPID%
JOBNAME=%JOBNAME%

logs_dir=${HPCROOTDIR}/LOG_${EXPID}
configfile=$logs_dir/${JOBNAME}_config

source ${HPCROOTDIR}/lib/MARENOSTRUM5/util.sh
conda_init
conda activate /gpfs/scratch/bsc32/bsc032376/envs/neuralgcm

python3 $HPCROOTDIR/lib/sim_neuralgcm.py -c $configfile
