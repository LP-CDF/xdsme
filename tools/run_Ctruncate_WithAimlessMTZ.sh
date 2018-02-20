#!/bin/bash

if [ $# -eq 0 ] ; then
  echo " Need aimless file as input"
  exit 1
fi

function run_ctruncate() {
PREFIX=$(basename $1 .mtz)
ctruncate -hklin $1 \
          -hklout ${PREFIX}_ctruncate.mtz \
          -colin '/*/*/[IMEAN,SIGIMEAN]' \
          -colano  '/*/*/[I(+),SIGI(+),I(-),SIGI(-)]' \
          |tee ${PREFIX}_truncate.log
}
run_ctruncate $1
