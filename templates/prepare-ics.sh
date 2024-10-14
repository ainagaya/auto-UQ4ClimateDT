#!/bin/bash

# PREPARE-ICS

DATE=%CHUNK_START_DATE%
TIME=%CHUNK_START_HOUR%
INPDIR=%DIRS.INPUT_DIR%
FDB_PATH=%DIRS.FDB_PATH%
SOURCESTREAM=regularll
BUNDLEDIR=%DIRS.BUNDLE_DIR%
SUBCENTRE=1003

conda

# -------------------------------------------------------------------------------------------------------------------- #
mkdir -p ${OUTDIR}
cd ${OUTDIR}

export ECCODES_DEFINITION_PATH=${BUNDLEDIR}/source/eccodes/definitions

# Need FDB(?)
export FDB_HOME=${FDB_PATH}/${SOURCESTREAM}
BINDIR=${BUNDLEDIR}/build/bin/
${BINDIR}/fdb-info --all

VAR2D=228

cat<<EOF >mars_sfc_${DATE}_${TIME}
retrieve,
  class=d1,
  dataset=climate-dt,
  activity=ScenarioMIP,
  experiment=SSP3-7.0,
  generation=1,
  model=IFS-FESOM,
  realization=1,
  resolution=standard,
  expver=hz9o,
  type=fc,
  stream=clte,
  levtype=sfc,
  target=graphcast_sfc_tp_${DATE}_${TIME}.grib,
  param=${VAR2D},
  date=${DATE},
  time=${TIME},
  repres=GG,
  domain=G,
  resol=AUTO,
  area=90.0/0.0/-90.0/360.0,
  packing=simple
EOF

${BINDIR}/fdb-read --raw mars_sfc_${DATE}_${TIME} graphcast_sfc_tp_${DATE}_${TIME}.grib
