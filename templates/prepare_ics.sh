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
    grid=$(awk -F= '/grid/ {gsub(/,/, "", $2); print $2}' $file)

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
    # if levtype is sfc, then we need to modify the typeOfLevel
    #if [ $levtype == "sfc" ]; then
    #    ${BINDIR}/grib_set -s typeOfLevel=surface ${AI_MODEL}_${levtype}_${DATE:0:8}_${TIME}_${file_num}.grib ${AI_MODEL}_${levtype}_${DATE:0:8}_${TIME}_${file_num}_fix.grib
    #    mv ${AI_MODEL}_${levtype}_${DATE:0:8}_${TIME}_${file_num}_fix.grib ${AI_MODEL}_${levtype}_${DATE:0:8}_${TIME}_${file_num}.grib
    #fi
done

# total column water needs to be computed from 5 constituents
cat<<EOF >mars_tcw
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
  levtype=sfc,
  param=137,
  date=${DATE:0:8},
  time=${TIME}/$((TIME-6)),
  repres=GG,
  domain=G,
  resol=AUTO,
  area=90.0/0.0/-90.0/360.0,
  packing=simple,
  fieldset=tcwv
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
  levtype=sfc,
  param=137,
  date=${DATE:0:8},
  time=${TIME}/$((TIME-6)),
  repres=GG,
  domain=G,
  resol=AUTO,
  area=90.0/0.0/-90.0/360.0,
  packing=simple,
  param=78,
  fieldset=tclw
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
  levtype=sfc,
  param=137,
  date=${DATE:0:8},
  time=${TIME}/$((TIME-6)),
  repres=GG,
  domain=G,
  resol=AUTO,
  area=90.0/0.0/-90.0/360.0,
  packing=simple,
  param=79,
  fieldset=tciw
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
  levtype=sfc,
  param=137,
  date=${DATE:0:8},
  time=${TIME}/$((TIME-6)),
  repres=GG,
  domain=G,
  resol=AUTO,
  area=90.0/0.0/-90.0/360.0,
  packing=simple,
  param=228089,
  fieldset=tcrw
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
  levtype=sfc,
  param=137,
  date=${DATE:0:8},
  time=${TIME}/$((TIME-6)),
  repres=GG,
  domain=G,
  resol=AUTO,
  area=90.0/0.0/-90.0/360.0,
  packing=simple,
  param=228090,
  fieldset=tcsw
compute,
   formula  = "tcwv+tclw+tciw+tcrw+tcsw",
   target   = "tcw"
EOF

# this containes tcw but also the other fields
${BINDIR}/fdb-read --raw mars_tcw ${AI_MODEL}_sfc_${DATE:0:8}_${TIME}_tcw_tmp.grib
/gpfs/projects/ehpc01/dte/mars/versions/6.99.2.0/bin/grib_set -s shortName=tcw ${AI_MODEL}_sfc_${DATE:0:8}_${TIME}_tcw_tmp.grib ${AI_MODEL}_sfc_${DATE:0:8}_${TIME}_tcw.grib

# we need to extract tcw
#/gpfs/projects/ehpc01/dte/mars/versions/6.99.2.0/bin/grib_copy -w shortName=tcw ${AI_MODEL}_sfc_${DATE:0:8}_${TIME}_tcw_tmp.grib ${AI_MODEL}_sfc_${DATE:0:8}_${TIME}_tcw.grib

#${BINDIR}/grib_set -s shortName=tcw,typeOfLevel=surface ${AI_MODEL}_sfc_${DATE:0:8}_${TIME}_tcw_tmp.grib ${AI_MODEL}_sfc_${DATE:0:8}_${TIME}_tcw.grib
#rm mars_tcw ${AI_MODEL}_sfc_${DATE:0:8}_${TIME}_tcw_tmp.grib
mv ${AI_MODEL}_sfc_${DATE:0:8}_${TIME}_tcw_tmp.grib REMOVE_ME_${AI_MODEL}_sfc_${DATE:0:8}_${TIME}_tcw_tmp.grib

# Merge all the files
cat ${INPDIR}/${AI_MODEL}_*_${DATE:0:8}_${TIME}_*.grib > ${INPDIR}/${AI_MODEL}_${DATE:0:8}_${TIME}.grib

## Need to duplicate z and lsm to time 0600
/gpfs/projects/ehpc01/dte/mars/versions/6.99.2.0/bin/grib_copy -w param=172 ${INPDIR}/${AI_MODEL}_${DATE:0:8}_${TIME}.grib ${INPDIR}/${AI_MODEL}_${DATE:0:8}_${TIME}_lsm.grib
/gpfs/projects/ehpc01/dte/mars/versions/6.99.2.0/bin/grib_copy -w param=129 ${INPDIR}/${AI_MODEL}_${DATE:0:8}_${TIME}.grib ${INPDIR}/${AI_MODEL}_${DATE:0:8}_${TIME}_z.grib
/gpfs/projects/ehpc01/dte/mars/versions/6.99.2.0/bin/grib_set -s time="600" "${INPDIR}/${AI_MODEL}_${DATE:0:8}_${TIME}_lsm.grib" ${INPDIR}/${AI_MODEL}_${DATE:0:8}_${TIME}_lsm_0600.grib
/gpfs/projects/ehpc01/dte/mars/versions/6.99.2.0/bin/grib_set -s time="600" "${INPDIR}/${AI_MODEL}_${DATE:0:8}_${TIME}_z.grib" ${INPDIR}/${AI_MODEL}_${DATE:0:8}_${TIME}_z_0600.grib


# Join the files
cat ${INPDIR}/${AI_MODEL}_${DATE:0:8}_${TIME}_lsm_0600.grib ${INPDIR}/${AI_MODEL}_${DATE:0:8}_${TIME}_z_0600.grib >> ${INPDIR}/${AI_MODEL}_${DATE:0:8}_${TIME}.grib

TARGETNGRID=320

# remap to target N grid
${BINDIR}/mir --reduced=${TARGETNGRID} ${INPDIR}/${AI_MODEL}_${DATE:0:8}_${TIME}.grib ${INPDIR}/${AI_MODEL}_${DATE:0:8}_${TIME}_N${TARGETNGRID}.grib

# Add missing fields
${BINDIR}/grib_set -s date=${DATE:0:8},time=600,subCentre=${SUBCENTRE} ${HPCROOTDIR}/../aifs-initial-from-fdb/data/aifs_lsm_slor_sdor_z.N${TARGETNGRID}.grib2 aifs_external.N${TARGETNGRID}_1.grib
${BINDIR}/grib_set -s date=${DATE:0:8},time=$((TIME-6)),subCentre=${SUBCENTRE} ${HPCROOTDIR}/../aifs-initial-from-fdb/data/aifs_lsm_slor_sdor_z.N${TARGETNGRID}.grib2 aifs_external.N${TARGETNGRID}_2.grib
#${BINDIR}/grib_copy -B'level:i asc' aifs_combined_N${TARGETNGRID}.grib aifs_external.N${TARGETNGRID}_1.grib aifs_external.N${TARGETNGRID}_2.grib aifs-nextgems-production-${DATE}-${TIME1}-${TIME2}.grib2


cat aifs_external.N${TARGETNGRID}_1.grib aifs_external.N${TARGETNGRID}_2.grib >> ${INPDIR}/${AI_MODEL}_${DATE:0:8}_${TIME}_N${TARGETNGRID}.grib


#convert to grib 1
# currently failing, i will have to remove the fields tcwat and maybe some more
${BINDIR}/grib_set -s edition=1 ${INPDIR}/${AI_MODEL}_${DATE:0:8}_${TIME}_N${TARGETNGRID}.grib ${INPDIR}/${AI_MODEL}_${DATE:0:8}_${TIME}_N${TARGETNGRID}.grib1
mv ${INPDIR}/${AI_MODEL}_${DATE:0:8}_${TIME}_N${TARGETNGRID}.grib1 ${INPDIR}/${AI_MODEL}_${DATE:0:8}_${TIME}_N${TARGETNGRID}.grib
