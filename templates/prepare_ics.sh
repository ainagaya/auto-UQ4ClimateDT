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

## AI-MODEL
AI_MODEL=%AI_MODEL%
AI_CHECKPOINT=%AI_CHECKPOINT%


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
conda activate /gpfs/projects/bsc32/ml_models/emulator_models/ecmwf_ai_models/wf_emulator_snake_2

export ECCODES_DEFINITION_PATH=${BUNDLEDIR}/source/eccodes/definitions

# Need FDB(?)
export FDB_HOME=${FDB_PATH}/${SOURCESTREAM}
BINDIR=${BUNDLEDIR}/build/bin/
${BINDIR}/fdb-info --all

mkdir -p ${INPDIR}
cd ${INPDIR}

ai-models ${AI_MODEL} --retrieve-requests --checkpoint ${AI_CHECKPOINT} > ${INPDIR}/retrieve_requests.txt
# Read retrieve_requests.txt and process each block
awk -v RS= '{print > "mars_" NR ".txt"}' ${INPDIR}/retrieve_requests.txt

# Process each generated file
for file in ${INPDIR}/mars_*.txt; do
    levelist=$(awk -F= '/levelist/ {gsub(/,/, "", $2); print $2}' $file)
    levtype=$(awk -F= '/levtype/ {gsub(/,/, "", $2); print $2}' $file)
    param=$(awk -F= '/param/ {gsub(/,/, "", $2); print $2}' $file)

    file_num=$(echo $file | awk -F_ '{print $2}' | awk -F. '{print $1}')
    
    cat <<EOF > ${INPDIR}/request_${file_num}
retrieve,
   database=latlon,
   class=${CLASS},
   dataset=${DATASET},
   activity=${ACTIVITY},
   experiment=${EXPERIMENT},
   levelist=${levelist},
   levtype=${levtype},
   param=${param},
   generation=${GENERATION},
   model=${MODEL},
   realization=${REALIZATION},
   resolution=${RESOLUTION},
   expver=${EXPVER},
   type=${TYPE},
   stream=${STREAM},
   target=${AI_MODEL}_${levtype}_${DATE:0:8}_${TIME}_${file_num}.grib,
   date=${DATE:0:8},
   time=${TIME}/$((TIME-6)),
   repres=GG,
   domain=G,
   resol=AUTO,
   packing=simple
EOF
    /gpfs/projects/ehpc01/dte/bin/mars ${INPDIR}/request_${file_num}
done

## Need to duplicate z and lsm to time 0600
for file in ${INPDIR}/${AI_MODEL}_*_${DATE:0:8}_${TIME}_*.grib; do
    grib_copy -w param=172 $file ${file}_lsm
    grib_copy -w param=129 $file ${file}_z
    grib_set -s time="${TIME}" "${file}_lsm" ${file}_lsm_0600
    grib_set -s time="${TIME}" "${file}_z" ${file}_z_0600
done

# Merge all the files
cat ${INPDIR}/${AI_MODEL}_*_${DATE:0:8}_${TIME}_*.grib > ${INPDIR}/${AI_MODEL}_${DATE:0:8}_${TIME}.grib
