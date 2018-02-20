#!/bin/bash

# Little utility to run STARANISO from AutoPROC.
# This script follows the protocol developped by GLOBALPHASING for unmerged data
# For more information see http://staraniso.globalphasing.org/staraniso_about.html
# Script delivered as with no warranty on its use and the use of its outputs.

#__version__ = "0.0.1"
#__date__ = "19-02-2018"
#__author_="Ludovic Pecqueur"
#__license__ = "New BSD http://www.opensource.org/licenses/bsd-license.php"

echo "
This script should be used on uncut but scaled datasets ie full resolution range using XDS_ASCII.HKL or XXXXX_pointless.mtz as input
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

OUTPUTDIR=$(dirname ${HKLIN})/STARANISO

if [ ! -f ${OUTPUTDIR} ]; then
	mkdir $(dirname ${HKLIN})/STARANISO
	mkdir $(dirname ${HKLIN})/STARANISO/MOL2
fi
##########################################################################

#Determine initial anisotropic mask
function run_staraniso_1() {
staraniso \
HKLIN ${PREFIX}_aimless.mtz \
HKLOUT ${OUTPUTDIR}/${PREFIX}-staraniso-merged-aniso.mtz \
MSKOUT ${OUTPUTDIR}/${PREFIX}-staraniso-merged-aniso.msk \
RESOUT ${OUTPUTDIR}/${PREFIX}-staraniso-merged-aniso.res \
RLAXES ${OUTPUTDIR}/MOL2/${PREFIX}-staraniso-merged-aniso-rlaxes \
REDUND ${OUTPUTDIR}/MOL2/${PREFIX}-staraniso-merged-aniso-redund \
ISMEAN ${OUTPUTDIR}/MOL2/${PREFIX}-staraniso-merged-aniso-ismean \
DWFACT ${OUTPUTDIR}/MOL2/${PREFIX}-staraniso-merged-aniso-dwfact \
ELLIPS ${OUTPUTDIR}/MOL2/${PREFIX}-staraniso-merged-aniso-ellips << eof 
end
eof
}

#Apply this mask to unmerged data
function run_staraniso_2() {
staraniso \
HKLIN ${HKLIN2} \
MSKIN ${OUTPUTDIR}/${PREFIX}-staraniso-merged-aniso.msk \
HKLOUT ${OUTPUTDIR}/${PREFIX}-staraniso-masked-aniso.mtz \
RESOUT ${OUTPUTDIR}/${PREFIX}-staraniso-masked-aniso.res \
RLAXES ${OUTPUTDIR}/MOL2/${PREFIX}-staraniso-masked-aniso-rlaxes \
DWFACT ${OUTPUTDIR}/MOL2/${PREFIX}-staraniso-masked-aniso-dwfact <<eof
end
eof
}

#Determine scales after anisotropic cut-off
function run_aimless_1() {
aimless HKLIN ${OUTPUTDIR}/${PREFIX}-staraniso-masked-aniso.mtz \
        HKLOUT ${OUTPUTDIR}/${PREFIX}-staraniso-masked-scaled.mtz \
	SCALES ${OUTPUTDIR}/${PREFIX}-staraniso-masked-scaled.scales <<eof
	INIT UNIT
	BINS 10 INTE 10
	SCAL ABSO 6
	ANOM
eof
}

if [ ${HKLIN} = "XDS_ASCII.HKL" ]; then
	HKLIN2=${PREFIX}_pointless.mtz
else
	HKLIN2=$1
fi

#Apply these scales to all data
function run_aimless_2() {
aimless HKLIN ${HKLIN2} \
       HKLOUT ${OUTPUTDIR}/${PREFIX}-staraniso-masked-merged.mtz <<eof
       ONLY
       BINS 10 INTE 10
       REST ${OUTPUTDIR}/${PREFIX}-staraniso-masked-scaled.scales
       SCAL ABSO 6
       ANOM
       OUTP UNME
eof
mv ${OUTPUTDIR}/${PREFIX}-staraniso-masked-merged_unmerged.mtz ${OUTPUTDIR}/${PREFIX}-staraniso-masked-unmerged.mtz
}

#Output final mask & anisotropy-corrected Fs
function run_staraniso_3() {
staraniso \
HKLIN  ${OUTPUTDIR}/${PREFIX}-staraniso-masked-merged.mtz \
RESOUT ${OUTPUTDIR}/${PREFIX}-staraniso-aniso-merged.res \
BINOUT ${OUTPUTDIR}/bins.txt \
RLAXES ${OUTPUTDIR}/MOL2/${PREFIX}-staraniso-aniso-merged-rlaxes \
REDUND ${OUTPUTDIR}/MOL2/${PREFIX}-staraniso-aniso-merged-redund \
ELLIPS ${OUTPUTDIR}/MOL2/${PREFIX}-staraniso-aniso-merged-ellips \
ISMEAN ${OUTPUTDIR}/MOL2/${PREFIX}-staraniso-aniso-merged-ismean \
DWFACT ${OUTPUTDIR}/MOL2/${PREFIX}-staraniso-aniso-merged-dwfact \
HKLOUT ${OUTPUTDIR}/${PREFIX}-staraniso-aniso-merged.mtz \
MSKOUT ${OUTPUTDIR}/${PREFIX}-staraniso-aniso-merged.msk <<eof
end
eof
}

run_staraniso_1 ${HKLIN} |tee ${OUTPUTDIR}/${PREFIX}_staraniso.log
run_staraniso_2 ${HKLIN2} |tee -a ${PREFIX}_staraniso.log
run_aimless_1 |tee ${OUTPUTDIR}/${PREFIX}-staraniso-masked-scaled.log
run_aimless_2 |tee ${OUTPUTDIR}/${PREFIX}-staraniso-masked-merged.log
run_staraniso_3 |tee ${OUTPUTDIR}/${PREFIX}_staraniso_aniso_merged.log

echo "You can use the file ${OUTPUTDIR}/${PREFIX}-staraniso-aniso-merged.mtz for refinement with BUSTER"
echo '''
If using this file please cite :

"Tickle, I.J., Flensburg, C., Keller, P., Paciorek, W., Sharff, A.,
Vonrhein, C., Bricogne, G. (2018). STARANISO. Cambridge, United
Kingdom: Global Phasing Ltd."

'''
