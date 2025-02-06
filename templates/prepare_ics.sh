#!/bin/bash

# PREPARE-ICS

HPCROOTDIR=%HPCROOTDIR%
START_DATE=%CHUNK_START_DATE%
TIME1=%CHUNK_START_HOUR%
END_DATE=%CHUNK_END_DATE%
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

# Variables
VAR2D=%VARIABLES.VAR2D%
VAR3D=%VARIABLES.VAR3D%
PLEVELS=%VARIABLES.PLEVELS%

## AI-MODEL
AI_MODEL=%AI_MODEL%
AI_CHECKPOINT=%AI_CHECKPOINT%

export ECCODES_DEFINITION_PATH=${BUNDLEDIR}/source/eccodes/definitions

export FDB_HOME=${FDB_PATH}/${SOURCESTREAM}
BINDIR=${BUNDLEDIR}/build/bin/
${BINDIR}/fdb-info --all

# keep only the 8 first characters of the date
START_DATE=${START_DATE:0:8}
END_DATE=${END_DATE:0:8}

mkdir -p ${INPDIR}
cd ${INPDIR}

TIME2=$(( TIME1 + 6 ))

TIME1=${TIME1}00
TIME2=${TIME2}00

TIME="${TIME1}/${TIME2}"

# Get the directory of the script
SCRIPT_DIR="${HPCROOTDIR}/lib"

# Path of the constant variables file
SCRDIR="/gpfs/scratch/bsc32/bsc032376/aifs-initial-from-fdb/data"

TARGETNGRID=320

SUBCENTRE=1003


# After this, modify also the OUTDIR variable in the main code (retrieve_aifs_inputs.sh)
# Additionally, make sure that the path to the constant orography file in functions.sh (add_subgrid_info()) is correct.

# Functions
source "${SCRIPT_DIR}/functions.sh"

# Main execution
main() {
    setup_environment
    process_date_range
}

setup_environment() {
    YYYY=$(echo $START_DATE | cut -c1-4)
    OUTDIR="${INPDIR}/${ACTIVITY}_${EXPERIMENT}_${YYYY}/"
    mkdir -p "${OUTDIR}"
    cd "${OUTDIR}" || exit 1

}

process_date_range() {
    START=$(date -d "$START_DATE" +%s)
    END=$(date -d "$END_DATE" +%s)

    for (( CURRENT_DATE=$START; CURRENT_DATE<=$END; CURRENT_DATE+=86400 )); do
        DATE=$(date -d "@${CURRENT_DATE}" +%Y%m%d)
        echo "Processing date: $DATE"
        process_single_date "$DATE"
    done
}

process_single_date() {
    local DATE=$1
    retrieve_surface_data "$DATE"
    retrieve_tcw_data "$DATE"
    retrieve_pressure_level_data "$DATE"
    combine_and_remap "$DATE"
    add_subgrid_info "$DATE"
    create_final_output "$DATE"
}

main "$@"

# #####################################################
# # Initializes conda
# # Globals:
# #
# # Arguments:
# #
# #####################################################
# function conda_init() {
#     set +xuve
#     # >>> conda initialize >>>
#     # !! Contents within this block are managed by 'conda init' !!
#     __conda_setup="$('/apps/GPP/ANACONDA/2023.07/bin/conda' 'shell.bash' 'hook' 2>/dev/null)"
#     if [ $? -eq 0 ]; then
#         eval "$__conda_setup"
#     else
#         if [ -f "/apps/GPP/ANACONDA/2023.07/etc/profile.d/conda.sh" ]; then
#             . "/apps/GPP/ANACONDA/2023.07/etc/profile.d/conda.sh"
#         else
#             export PATH="/apps/GPP/ANACONDA/2023.07/bin:$PATH"
#         fi
#     fi
#     unset __conda_setup
#     set -xuve

# }

# conda_init
# conda activate /gpfs/projects/bsc32/ml_models/emulator_models/ecmwf_ai_models/wf_emulator_snake_2


# ai-models ${AI_MODEL} --retrieve-requests --checkpoint ${AI_CHECKPOINT} > ${INPDIR}/retrieve_requests.txt
# # Read retrieve_requests.txt and process each block
# awk -v RS= '{print > "mars_" NR ".txt"}' ${INPDIR}/retrieve_requests.txt

# Process each generated file
# for file in ${INPDIR}/mars_*.txt; do
#     levelist=$(awk -F= '/levelist/ {gsub(/,/, "", $2); print $2}' $file)
#     levtype=$(awk -F= '/levtype/ {gsub(/,/, "", $2); print $2}' $file)
#     param=$(awk -F= '/param/ {gsub(/,/, "", $2); print $2}' $file)
#     grid=$(awk -F= '/grid/ {gsub(/,/, "", $2); print $2}' $file)

#     file_num=$(echo $file | awk -F_ '{print $2}' | awk -F. '{print $1}')
    
#     cat <<EOF > ${INPDIR}/request_${file_num}
# retrieve,
#    database=latlon,
#    class=${CLASS},
#    dataset=${DATASET},
#    activity=${ACTIVITY},
#    experiment=${EXPERIMENT},
#    levelist=${levelist},
#    levtype=${levtype},
#    param=${param},
#    generation=${GENERATION},
#    model=${MODEL},
#    realization=${REALIZATION},
#    resolution=${RESOLUTION},
#    expver=${EXPVER},
#    type=${TYPE},
#    stream=${STREAM},
#    target=${AI_MODEL}_${levtype}_${DATE:0:8}_${TIME}_${file_num}.grib,
#    date=${DATE:0:8},
#    time=${TIME}/$((TIME-6)),
#    repres=GG,
#    domain=G,
#    resol=AUTO,
#    packing=simple
# EOF
#     /gpfs/projects/ehpc01/dte/bin/mars ${INPDIR}/request_${file_num}
#     # if levtype is sfc, then we need to modify the typeOfLevel
#     #if [ $levtype == "sfc" ]; then
#     #    ${BINDIR}/grib_set -s typeOfLevel=surface ${AI_MODEL}_${levtype}_${DATE:0:8}_${TIME}_${file_num}.grib ${AI_MODEL}_${levtype}_${DATE:0:8}_${TIME}_${file_num}_fix.grib
#     #    mv ${AI_MODEL}_${levtype}_${DATE:0:8}_${TIME}_${file_num}_fix.grib ${AI_MODEL}_${levtype}_${DATE:0:8}_${TIME}_${file_num}.grib
#     #fi
# done

