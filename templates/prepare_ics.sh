#!/bin/bash

# PREPARE-ICS

HPCROOTDIR=%HPCROOTDIR%
DATE=%CHUNK_START_DATE%
TIME=%CHUNK_START_HOUR%
INPDIR=%DIRS.INPUT_DIR%
FDB_PATH=%DIRS.FDB_PATH%
SOURCESTREAM=regularll
BUNDLEDIR=%DIRS.BUNDLE_DIR%
SUBCENTRE=1003

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
LEVTYPE=%REQUEST.LEVTYPE%

## AI-MODEL
AI_MODEL=%AI_MODEL%


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

conda_init
conda activate ai-models

mkdir -p ${INPDIR}
cd ${INPDIR}

export ECCODES_DEFINITION_PATH=${BUNDLEDIR}/source/eccodes/definitions

# Need FDB(?)
export FDB_HOME=${FDB_PATH}/${SOURCESTREAM}
BINDIR=${BUNDLEDIR}/build/bin/
${BINDIR}/fdb-info --all

VAR2D=228

cat<<EOF >mars_sfc_${DATE}_${TIME}
retrieve,
  class=${CLASS},
  dataset=${DATASET},
  activity=${ACTIVITY},
  experiment=${EXPERIMENT},
  generation=${GENERATION},
  model=${MODEL},
  realization=${REALIZATION},
  resolution=${RESOLUTION},
  expver=${EXPVER},
  type=${TYPE},
  stream=${STREAM},
  levtype=${LEVTYPE},
  target=${AI_MODEL}_${LEVTYPE}_tp_${DATE}_${TIME}.grib,
  param=${VAR2D},
  date=${DATE},
  time=${TIME},
  repres=GG,
  domain=G,
  resol=AUTO,
  area=90.0/0.0/-90.0/360.0,
  packing=simple
EOF

${BINDIR}/fdb-read --raw mars_${LEVTYPE}_${DATE}_${TIME} ${AI_MODEL}_${LEVTYPE}_tp_${DATE}_${TIME}.grib
