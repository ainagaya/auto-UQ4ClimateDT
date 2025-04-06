#!/bin/bash

# SIM neuralgcm

HPCROOTDIR=%HPCROOTDIR%
EXPID=%DEFAULT.EXPID%
JOBNAME=%JOBNAME%

SIF_PATH=/gpfs/scratch/ehpc204/bsc032376/neuralgcm_bsc_v1.0.sif

JOBNAME_WITHOUT_EXPID=$(echo ${JOBNAME} | sed 's/^[^_]*_//')

logs_dir=${HPCROOTDIR}/LOG_${EXPID}
configfile=$logs_dir/config_neuralgcm_${JOBNAME_WITHOUT_EXPID}

module load cuda
source ${HPCROOTDIR}/lib/MARENOSTRUM5/util.sh
# conda_init
# conda activate /gpfs/scratch/bsc32/bsc032376/envs/neuralgcm

module load singularity

singularity exec --nv --bind $HPCROOTDIR/lib --bind $logs_dir --env HPCROOTDIR=$HPCROOTDIR --env configfile=$configfile \
    ${SIF_PATH} python3 $HPCROOTDIR/runscripts/sim_neuralgcm.py -c $configfile

