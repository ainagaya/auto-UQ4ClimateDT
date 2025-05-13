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
AI_CHECKPOINT=%MODEL.CHECKPOINT%
TARGETGRID=%VARIABLES.TARGETGRID%
DELAY=%MODEL.DELAY%

MEMBER=%MEMBER%

export ECCODES_DEFINITION_PATH=${BUNDLEDIR}/source/eccodes/definitions

export FDB_HOME=${FDB_PATH}/${SOURCESTREAM}
BINDIR=${BUNDLEDIR}/build/bin/
#${BINDIR}/fdb-info --all

# keep only the 8 first characters of the date
START_DATE=${START_DATE:0:8}
END_DATE=${END_DATE:0:8}

mkdir -p ${INPDIR}
cd ${INPDIR}

TIME2=$(( TIME1 + DELAY ))

TIME1=${TIME1}00
TIME2=${TIME2}00

TIME="${TIME1}/${TIME2}"

# Get the directory of the script
SCRIPT_DIR="${HPCROOTDIR}/lib"

# Path of the constant variables file
SCRDIR="/gpfs/scratch/bsc32/bsc032376/aifs-initial-from-fdb/data"

SUBCENTRE=1003


# After this, modify also the OUTDIR variable in the main code (retrieve_aifs_inputs.sh)
# Additionally, make sure that the path to the constant orography file in functions.sh (add_subgrid_info()) is correct.

# Functions
source "${SCRIPT_DIR}/functions.sh"

module load intel
module load impi

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
        DATE=$(date -d "@${CURRENT_DATE}" +%%Y%%m%%d)
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
