#!/usr/bin/env python
# -*- coding: utf-8 -*

__version__ = "0.1.0"
__author__ = "Pecqueur Ludovic"
__date__ = "20-12-2018"
__copyright__ = "Copyright (c) 2018"
__license__ = "New BSD http://www.opensource.org/licenses/bsd-license.php"

import os, sys, platform
import re

_use_pylab=0
try:
	from matplotlib.pylab import *
	_use_pylab=1
except:
	pass

########################################################################################
def usage():
    print '''
             ###########################################################
              USAGE: ./XDSplotter_xdsme.py
              Input file : INTEGRATE.LP
	      Ouptutfile: frames.scales
	      xdsstat must be in PATH and called by:
	      'xdsstat' for Linux
	      'xdsstat-i386-mac' for mac
	     ###########################################################
	     '''
    sys.exit()



def existe_file(fname):
	"Verifie l'existence du fichier"
	try :
		fo = open(fname, 'r')
		fo.close
		return 1
	except :
		return 0

def which(program):
	'''Check if program is in PATH
	taken from https://stackoverflow.com/questions/377017/test-if-executable-exists-in-python
	'''
	import os
	def is_exe(fpath):
		return os.path.isfile(fpath) and os.access(fpath, os.X_OK)
	fpath, fname = os.path.split(program)
    	if fpath:
        	if is_exe(program):
            		return program
    	else:
        	for path in os.environ["PATH"].split(os.pathsep):
            		exe_file = os.path.join(path, program)
            		if is_exe(exe_file):
                		return exe_file
	return None

def run_xdsstat():
	'''Run XDSSTAT'''
	import subprocess, sys
	OStype=platform.system()
	if OStype=="Darwin":
		p = subprocess.Popen('xdsstat-i386-mac > XDSSTAT.LP', stdin=subprocess.PIPE, shell=True).communicate(input='\n')
	elif OStype=="Linux":
		p = subprocess.Popen('xdsstat > XDSSTAT.LP', stdin=subprocess.PIPE, shell=True).communicate(input='\n')
	else:
		print "xdsstat binary not found in PATH"
		sys.exit()

def Read_INTEGRATE(inputlist):
	#PARSING all_lines to RETRIEVE RELEVANT DATA
	relevantdata=re.compile(' .....   0 ...... ........   ..  .....    ....   ...  .......  .......')
	fd = open("frames.scales", 'w')
	DataDict={}
	for i in inputlist:
		#print i
		if relevantdata.match(i):
			#print "YES"
			fd.write(i)
			Data={}
			col=i.split()
			counter=int(col[0])
			Data['IMAGE']=col[0]
			Data['IER']=col[1]
			Data['SCALE']=col[2]
			Data['NBKG']=col[3]
			Data['NOVL']=col[4]
			Data['NEWALD']=col[5]
			Data['NSTRONG']=col[6]
			Data['NREJ']=col[7]
			Data['DIVERGENCE']=col[8]
			Data['MOSAICITY']=col[9]
			DataDict[counter]=Data
	fd.close()
	return DataDict

def Read_XDSSTAT():
	import re
	fe= open('XDSSTAT.LP','r')
	all_lines=fe.readlines()
	#print all_lines
	fe.close()
	Table1=re.compile(' L$')
	DataDict={}
	for i in all_lines:
		if Table1.search(i):
			#print i
			#fd.write(i)
			Data={}
			col=i.split()
			frame=int(col[0])
			Data['FRAME']=col[0]
			Data['REFS']=col[1]
			Data['MISFITS']=col[2]
			Data['IOBS']=col[3]
			Data['SIGMA']=col[4]
			Data['IOBS/SIGMA']=col[5]
			Data['PEAK']=col[6]
			Data['CORR']=col[7]
			Data['RMEAS']=col[8]
			Data['RmeasCOUNT']=col[9]
			Data['RmeasCOUNTUNIQUE']=col[10]
			DataDict[frame]=Data
	return DataDict	
		
def PylabPlot_all(DictXDSSTAT, DictINTEGRATE):
	import matplotlib.pyplot as plt
	import matplotlib.gridspec as gridspec
	frames, rmeas, iobssigma =([] for i in range(3))
	for u,v in DictXDSSTAT.iteritems():
		#print u
		frames.append(int(u))
		rmeas.append(float(v['RMEAS']))
		iobssigma.append(float(v['IOBS/SIGMA']))
		
	f1 = plt.figure(tight_layout=True, figsize=(12,8))
	gs = gridspec.GridSpec(3, 2)
	
	f1.canvas.set_window_title('CORRECT and XDSSTAT')
	ax1=f1.add_subplot(gs[0,0])
	ax1.plot(frames, rmeas,  marker='', linestyle='solid', linewidth=0.5, color='k', label='R_{meas}', markersize=2)
	ax1.set_ylabel('$R_{meas}$', fontsize=12,weight='bold', color='b')

	ax2=f1.add_subplot(gs[0,1])
	ax2.plot(frames, iobssigma,  marker='', linestyle='solid', linewidth=0.5, color='k', label='R_{meas}', markersize=2)
	ax2.set_ylabel('I/sig(I)', fontsize=12,weight='bold', color='b')

	frames, scalefactor, divergence, mosaicity, nstrong=[], [], [], [], []
	for u,v in DictINTEGRATE.iteritems():
		frames.append(int(u))
		scalefactor.append(float(v['SCALE']))
		divergence.append(float(v['DIVERGENCE']))
		mosaicity.append(float(v['MOSAICITY']))
		nstrong.append(float(v['NSTRONG']))
	MIN_X=min(frames); MAX_X=max(frames)
	
	ax3=f1.add_subplot(gs[1,0])	
	ax3.plot(frames, scalefactor,  marker='o', linestyle='solid', linewidth=0.5, color='k', label='Scalefactor', markersize=2)
	#axis([MIN_X-0.025*MAX_X, MAX_X+0.025*MAX_X,-MAX_Y, +MAX_Y])
	ax3.set_ylabel('Scalefactor', fontsize=12,weight='bold', color='b')
	
	ax4=f1.add_subplot(gs[1,1])
	plt.plot(frames, divergence,  marker='', linestyle='solid', linewidth=0.5, color='k', label='Divergence', markersize=2)
	ax4.set_ylabel('Divergence', fontsize=12,weight='bold', color='b')
	
	ax5=f1.add_subplot(gs[2,0])
	ax5.plot(frames, mosaicity,  marker='', linestyle='solid', linewidth=0.5, color='k', label='Mosaicity', markersize=2)
	ax5.set_ylabel('Mosaicity (deg)', fontsize=12,weight='bold', color='b')
	xtext = xlabel('Frame', fontsize=12,weight='bold', color='b')
	
	ax6=f1.add_subplot(gs[2,1])
	ax6.plot(frames, nstrong,  marker='', linestyle='solid', linewidth=0.5, color='k', label='Strong Ref', markersize=2)
	ax6.set_ylabel('# Strong Reflections', fontsize=12,weight='bold', color='b')
	xtext = xlabel('Frame', fontsize=12,weight='bold', color='b')
	plt.show()	
########################################################################################

#TODO: This HAS TO BE IMPROVED FOR binary existence check...
externaltool='xdsstat'
if which(externaltool) is None:
	print "\nWARNING: program %s not found, program aborted\n"%externaltool
	sys.exit()

inputfile='INTEGRATE.LP'
if existe_file(inputfile) ==0:
	print "File %s not found" % inputfile
	sys.exit()
else:
	with open(inputfile,'r') as f: 
		INTEGRATE=Read_INTEGRATE(f.readlines())

run_xdsstat()
XDSSTAT=Read_XDSSTAT()

if _use_pylab==1:
	PylabPlot_all(XDSSTAT, INTEGRATE)
else:
	print'''
File "%s" contains extracted DATA from INTEGRATE.LP
USE your favourite plotter to create graphs\n'''%('frames.scales')

########################################################################################
del XDSSTAT, INTEGRATE
