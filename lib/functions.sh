#!/bin/bash

retrieve_surface_data() {
    local DATE=$1
    cat <<EOF > mars_sfc
retrieve,
  class=d1,
  dataset=climate-dt,
  activity=${ACTIVITY},
  experiment=${EXPERIMENT},
  generation=1,
  model=${MODEL},
  realization=1,
  resolution=${RESOLUTION},
  expver=${EXPVER},
  type=fc,
  stream=clte,
  levtype=sfc,
  target=aifs_sfc.grib,
  param=${VAR2D},
  date=${DATE},
  time=${TIME}
EOF

    ${BINDIR}/fdb-read --raw mars_sfc aifs_sfc.grib
    rm mars_sfc
}

retrieve_tcw_data() {
    local DATE=$1
    cat <<EOF > mars_tcw
retrieve,
  class=d1,
  dataset=climate-dt,
  activity=${ACTIVITY},
  experiment=${EXPERIMENT},
  generation=1,
  model=${MODEL},
  realization=1,
  resolution=${RESOLUTION},
  expver=${EXPVER},
  type=fc,
  stream=clte,
  levtype=sfc,
  param=137,
  date=${DATE},
  time=${TIME},
  fieldset=tcwv
retrieve,
  param=78,
  fieldset=tclw
retrieve,
  param=79,
  fieldset=tciw
compute,
   formula  = "tcwv+tclw+tciw",
   target   = "tcw"
EOF

    ${BINDIR}/fdb-read --raw mars_tcw aifs_tcw_tmp.grib
    ${BINDIR}/grib_set -s shortName=tcw aifs_tcw_tmp.grib aifs_tcw.grib
    rm mars_tcw aifs_tcw_tmp.grib
}

retrieve_pressure_level_data() {
    local DATE=$1
    cat <<EOF > mars_pl
retrieve,
  class=d1,
  dataset=climate-dt,
  activity=${ACTIVITY},
  experiment=${EXPERIMENT},
  generation=1,
  model=${MODEL},
  realization=1,
  resolution=${RESOLUTION},
  expver=${EXPVER},
  type=fc,
  stream=clte,
  param=${VAR3D},
  levtype=pl,
  levelist=${PLEVELS},
  date=${DATE},
  time=${TIME}
EOF

    ${BINDIR}/fdb-read --raw mars_pl aifs_pl.grib
    rm mars_pl
}

combine_and_remap() {
    local DATE=$1
    ${BINDIR}/grib_copy -B'level:i asc' aifs_sfc.grib aifs_tcw.grib aifs_pl.grib combined_${SOURCESTREAM}.grib
    rm aifs_sfc.grib aifs_tcw.grib aifs_pl.grib

    ${BINDIR}/mir --reduced=${TARGETNGRID} combined_${SOURCESTREAM}.grib aifs_combined_N${TARGETNGRID}.grib
    mv combined_${SOURCESTREAM}.grib aimodels-climate-dt-${ACTIVITY}-${EXPERIMENT}-${DATE}-${TIME1}-${TIME2}.grib2
}

add_subgrid_info() {
    local DATE=$1
    ${BINDIR}/grib_set -s date=${DATE},time=${TIME1},subCentre=${SUBCENTRE} ${SCRDIR}/aifs_lsm_slor_sdor_z.N${TARGETNGRID}.grib2 aifs_external.N${TARGETNGRID}_1.grib
    ${BINDIR}/grib_set -s date=${DATE},time=${TIME2},subCentre=${SUBCENTRE} ${SCRDIR}/aifs_lsm_slor_sdor_z.N${TARGETNGRID}.grib2 aifs_external.N${TARGETNGRID}_2.grib
}

create_final_output() {
    local DATE=$1
    ${BINDIR}/grib_copy -B'level:i asc' aifs_combined_N${TARGETNGRID}.grib aifs_external.N${TARGETNGRID}_1.grib aifs_external.N${TARGETNGRID}_2.grib aifs-climate-dt-${ACTIVITY}-${EXPERIMENT}-${DATE}-${TIME1}-${TIME2}.grib2
    rm aifs_external.N${TARGETNGRID}_1.grib aifs_external.N${TARGETNGRID}_2.grib aifs_combined_N${TARGETNGRID}.grib

    ${BINDIR}/grib_set -s edition=1 aifs-climate-dt-${ACTIVITY}-${EXPERIMENT}-${DATE}-${TIME1}-${TIME2}.grib2 aifs-climate-dt-${ACTIVITY}-${EXPERIMENT}-${DATE}-${TIME1}-${TIME2}.grib1
    rm aifs-climate-dt-${ACTIVITY}-${EXPERIMENT}-${DATE}-${TIME1}-${TIME2}.grib2
}
