#!/bin/bash

if [ $# -eq 0 ] ; then
  HKLIN=helical_pos11_1_aimless.mtz
else
  HKLIN=$1
fi

function run_ctruncate() {
PREFIX=$(basename $1 .mtz)
ctruncate -hklin $1 \
          -hklout ${PREFIX}_ctruncate.mtz \
          -colin '/*/*/[IMEAN,SIGIMEAN]' \
          -colano  '/*/*/[I(+),SIGI(+),I(-),SIGI(-)]' \
          |tee Truncate.log
}
run_ctruncate $1
