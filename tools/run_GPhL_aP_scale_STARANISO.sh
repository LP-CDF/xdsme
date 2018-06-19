#!/bin/bash

# Little utility to run aP_scale from AutoPROC.
# AUTOPROC must be in the PATH
# For more information see http://staraniso.globalphasing.org

echo "
This script should be used on uncut, UNMERGED but scaled datasets ie full resolution range using XDS_ASCII.HKL or XXXXX_pointless.mtz as input
"

######################## IF XDS_ASCII.HKL as input #######################
if [ $# -eq 0 ]; then
  HKLIN=XDS_ASCII.HKL
else
  HKLIN=$1
fi

if [ ! -f ${HKLIN} ]; then
	echo "WARNING:
File ${HKLIN} not found, please check filename or PATH
	"
	exit 1
fi

function get_prefix {
   b=$(head  $1 | grep NAME_TEMPLATE_OF_DATA_FRAMES  | awk '{print $1}')
   test -z $b && b="XSCALE"                                             
   c=$(basename $b)                                                     
   echo ${c%_*.*}                                                       
}

if [ ${HKLIN} = "XDS_ASCII.HKL" ]; then
	PREFIX=$(get_prefix ${HKLIN})
	if [ ! -f ${PREFIX}_pointless.mtz ]; then
		pointless -copy XDSIN ${HKLIN} HKLOUT ${PREFIX}_pointless.mtz |tee ${PREFIX}_pointless.log
	else
		echo "
WARNING:
File ${PREFIX}_pointless.mtz exists skipping XDS_ASCII.HKL file conversion with POINTLESS
		"
	fi
else
	PREFIX=$(basename $1 _pointless.mtz)	
fi

BASEDIR="$( cd "$(dirname "${HKLIN}")" ; pwd -P )"		
OUTPUTDIR=${BASEDIR}/STARANISO

if [ ! -f ${OUTPUTDIR} ]; then
	mkdir ${BASEDIR}/STARANISO
fi

##########################################################################

function run_aP_scale() {
if [ ${HKLIN} = "XDS_ASCII.HKL" ]; then
	command="aP_scale -mtz ${BASEDIR}/${PREFIX}_pointless.mtz -P ${PREFIX} ${PREFIX} ${PREFIX} -id ${PREFIX} autoPROC_ScaleWithXscale=no"
else
	command="aP_scale -mtz ${BASEDIR}/${HKLIN} -P ${PREFIX} ${PREFIX} ${PREFIX} -id ${PREFIX} autoPROC_ScaleWithXscale=no"
fi
eval ${command}
}

cd ${OUTPUTDIR}
run_aP_scale

echo "You can use the file ${OUTPUTDIR}/${PREFIX}_staraniso_alldata.mtz for refinement with BUSTER"
echo '''
If using this file please cite :

"Vonrhein, C., Flensburg, C., Keller, P., Sharff, A., Smart, O.,
Paciorek, W., Womack, T. & Bricogne, G. (2011). Data processing and
analysis with the autoPROC toolbox. Acta Cryst. D67, 293-302."

AND

"Tickle, I.J., Flensburg, C., Keller, P., Paciorek, W., Sharff, A.,
Vonrhein, C., Bricogne, G. (2018). STARANISO. Cambridge, United
Kingdom: Global Phasing Ltd."

'''
cd ${BASEDIR}
echo "command line was: 
${command}
"

