#!/bin/bash

# SIM

DATE=%CHUNK_START_DATE%
TIME=%CHUNK_START_HOUR%
INPDIR=%DIRS.INPUT_DIR%
OUTDIR=%DIRS.OUTPUT_DIR%

conda activate ai-models

mkdir -p $OUTDIR
cd $OUTDIR

ai-models --file ${INPDIR}/aifs-nextgems-production-${DATE}-${TIME}.grib1 --path ${OUTDIR}/aifs-${DATE}-${TIME}.grib aifs
