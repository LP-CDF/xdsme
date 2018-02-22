#!/usr/bin/env python
# -*- coding: utf-8 -*-

__version__ = "0.1.0"
__author__ = "Pecqueur Ludovic"
__date__ = "09-02-2018"
__copyright__ = "Copyright (c) 2017-2018"
__license__ = "New BSD http://www.opensource.org/licenses/bsd-license.php"


import sys
import os

try:
    import numpy
except ImportError:
    raise ImportError('''%s
             Missing module numpy needed for option --CChalf
             %s'''%('='*47,'='*47))
try :
    from scipy import optimize
except :
    raise ImportError('''%s
             Missing module scipy.optimize needed for option --CChalf
             %s'''%('='*47,'='*47))
 
###############################################################################
class ExtractXDSCChalf:
    ''' '''
    def __init__(self, filename="", run_dir="",
                 verbose=False, raiseErrors=True):
        """ Extract relevant data from resum_scaling function in xupy
        """
        from xupy import resum_scaling
        self.resolution= []
        self.CChalf = []
        self.s=[]
        self.vector=[]
        self.HighResCChalf=float()
        self.HighRes=float()
        
        if not run_dir:
            run_dir = "./"
        self.run_dir = run_dir
        #
        full_filename = os.path.join(self.run_dir, filename)
        #
        if filename:
            try:
                fp = open(full_filename, "r")
                self.lp = fp.read()
                fp.close()
            except:
                raise IOError, "Can't read file: %s" % full_filename
        else:
            self.lp = ""

        if full_filename.count("CORRECT.LP"):
            self.s = resum_scaling(lpf=os.path.join(run_dir,"CORRECT.LP"))
            self.get_XDS_CChalf()
        else:
            if filename:
                raise IOError, "Don't know how to parse file: %s" % \
                               full_filename
                               
    def get_XDS_CChalf(self):
        if not self.s:
            print "\nERROR while running CORRECT"
            sys.exit()
        data=(self.s.last_table).splitlines()[3:-1] #discard total
        data=[ map(str, l.split()[0:15]) for l in data ]
        for i in data: 
            self.resolution.append(float(i[0]))
            self.CChalf.append(float(i[10].strip("*"))/100.)
            self.vector.append(1/(float(i[0]))**2)
        self.HighResCChalf=self.CChalf[-1]
        self.HighRes=self.resolution[-1]
        del self.s

class AimlessLogParser:
    """ A Parser for log file from AIMLESS.
    """
    def __init__(self, filename="", run_dir="",
                 verbose=False, raiseErrors=True):
        self.results = {}
        self.info = "AIMLESS Parser"
        self.fileType = "AIMLESS"
        self.verbose = verbose
        self.resolution = []
        self.CChalf= []
        #
        if not run_dir:
            run_dir = "./"
        self.run_dir = run_dir
        #
        full_filename = os.path.join(self.run_dir, filename)
        #
        if filename:
            try:
                fp = open(full_filename, "r")
                self.lp = fp.read()
                fp.close()
            except:
                raise IOError, "Can't read file: %s" % full_filename
        else:
            self.lp = ""

        if full_filename.count("aimless.log"):
            self.get_aimless_CChalf()
        else:
            if filename:
                raise IOError, "Don't know how to parse file: %s" % \
                               full_filename

    def get_aimless_CChalf(self):
        '''Parse AIMLESS log file for CChalf'''

        ### Select Diffraction range.
        sp1 = self.lp.index("  N  1/d^2    Dmid CCanom    Nanom   RCRanom   CC1/2   NCC1/2   Rsplit     CCfit CCanomfit   $$ $$")
        sp2 = self.lp.index("                   CCanom    Nanom   RCRanom   CC1/2   NCC1/2   Rsplit     CCfit CCanomfit", sp1)
        _table = self.lp[sp1:sp2].splitlines()[1:-2]
        _table = [ map(float, l.split()[1:]) for l in _table ]
        for l in _table:
            self.resolution.append(l[0])
            self.CChalf.append(l[5])

def func(x,d0,r):
    '''x and y are lists of same size
       x is 1/d**2, y is CC1/2
       d0 is 1/d**2 at half decrease
       r is the steepness of the falloff
    '''
    from scipy import tanh
    return 0.5*(1 -tanh((x - d0)/r))
    
def tanh_fit(Ex, Ey):
    '''Ex and Ey are lists of same size
       x is 1/d**2, y is CC1/2
       d0 is 1/d**2 at half decrease
       r is the steepness of the falloff
    '''
    from scipy.optimize import curve_fit
#    from pylab import plot
    
    #initializing parameters
    halffo=(max(Ey)-min(Ey))/2.
    DELTA=(max(Ey)-min(Ey))
    nearestpoint=int()
    for i in Ey:
        delta=abs(i - halffo)
        if delta<DELTA:
            DELTA=delta
            nearestpoint=Ey.index(i)
    d0=Ex[nearestpoint]
    r=0.1
    init_vals=[d0, r]
    p, pcov = curve_fit(func,Ex,Ey, p0=init_vals)
    d0_opt, r_opt=p[0], p[1]
#    plot(Ex, Ey, "wo", Ex, func(Ex,*p), "r-") # Plot of the data and the fit
    return [d0_opt, r_opt]
 
def EstimateCC_NewHighRes(cutoff, d0, r, Ey):
    '''Estimate a New High resolution
    cutoff based on CC1/2=value
    Ey is used to check if experimental data
    contain a CC1/2<Threshold, if not
    function is stopped
    '''
    from math import sqrt
    from scipy import tanh
    from numpy import linspace    

#Check if calculation is sensible or not
    if cutoff<=min(Ey):
        print "WARNING: data don't reach this cutoff value...skipping CC1/2 analysis"
        return
        
    cutoff=float(cutoff)
    d0=float(d0)
    r=float(r)
    HighRes=None
    CC_calc, delta=[], []
    #Searching for CC1/2 resolution by minimizing CC1/2-cutoff        
    x = linspace(0.,1.,1001).tolist()
    for val in x:
        CC_calc.append((0.5*(1 -tanh((val - d0)/r))))

    for val in CC_calc:
        delta.append(abs(val-cutoff))
    HighRes=round(sqrt(1/x[delta.index(min(delta))]),2)
    CalculatedCutoff=CC_calc[delta.index(min(delta))]          
    print '''   %s
   ->  Suggested New High Resolution Limit: %.2f A for CC1/2= %.2f <-
   %s
   ''' %('='*66,HighRes, CalculatedCutoff,'='*66)   
    return HighRes

def CalculateAimlessHighRes(filename, run_dir="./", verbose=1, CChalf=0.3):
    aimlessdata=AimlessLogParser(filename, run_dir, verbose) 
    fit=tanh_fit(aimlessdata.resolution,aimlessdata.CChalf)
    Newh=EstimateCC_NewHighRes(CChalf, fit[0], fit[1], aimlessdata.CChalf)
    return Newh

def CalculateXDSHighRes(xdsdata, CChalf=0.3): 
    fit=tanh_fit(xdsdata.vector,xdsdata.CChalf)
    Newh=EstimateCC_NewHighRes(CChalf, fit[0], fit[1], xdsdata.CChalf)
    return Newh
    
def CutXDSByCChalf(XDS_obj,filename="", run_dir="./", verbose=1, CChalf=0.3):
    '''Analyze XDS data and cut the data 
    to a cut off close to a defined CC1/2'''
    from XDS import run_xdsconv
    from pointless import run_aimless
    global RUN_XDSCONV, RUN_AIMLESS

    (l, h), spgn  = XDS_obj.run_pre_correct(cutres=False)
    XDS_obj.run_correct((l, h), spgn) #Cycle 1
    CChalf_data=ExtractXDSCChalf("CORRECT.LP", XDS_obj.run_dir, verbose)         
    Newh=CalculateXDSHighRes(CChalf_data, CChalf=CChalf)

    Cycle, MaxCycle =2,5
    if Newh is not None:
        print "Cycle %s of a maximum of %s"%(Cycle,MaxCycle)
        XDS_obj.run_correct((l, Newh), spgn) #Cycle 2
        Cycle+=1
        CChalf_data=ExtractXDSCChalf("CORRECT.LP", XDS_obj.run_dir)
        while Cycle <= MaxCycle :
            print "Cycle %s of a maximum of %s"%(Cycle,MaxCycle)
            oldHighRes=Newh
            Newh=CalculateXDSHighRes(CChalf_data, CChalf=CChalf)
            if oldHighRes == Newh and Newh != None:
                print "==>  CC1/2 High Resolution limit converged running AIMLESS and exporting to CCP4 format  <=="
                run_aimless(XDS_obj.run_dir)
                run_xdsconv(XDS_obj.run_dir)
                break
            elif Cycle==MaxCycle:
                print "==>  Maximum number of cycles reached, running last cycle, AIMLESS and exporting to CCP4 format  <=="
                RUN_AIMLESS=True
                RUN_XDSCONV=True
                XDS_obj.run_correct((l, Newh), spgn)
                break
            elif Newh == None:
                print "==>   Processed data using High Resolution limit of %.2f A, running AIMLESS and exporting to CCP4 format  <=="%oldHighRes
                run_aimless(XDS_obj.run_dir)                
                run_xdsconv(XDS_obj.run_dir)
                break
            else:
                XDS_obj.run_correct((l, Newh), spgn)
                Cycle+=1
    else:
        print "==>   Data processed using full resolution range --> exporting to CCP4 format   <=="
        run_xdsconv(XDS_obj.run_dir)
#                newrun.run_correct((l, h), spgn)
        
if __name__ == "__main__":   
#    inputfile=sys.argv[len(sys.argv)-1]
#    res = AimlessLogParser(filename="puck1_3_1_aimless.log", run_dir="/home/lpecqueur/XDSME_TEST/xdsme_TEST", verbose=1)
#    res2=tanh_fit(res.resolution,res.CChalf)
#    EstimateCC_NewHighRes(0.30, res2[0], res2[1], res.CChalf)
    res=ExtractXDSCChalf(filename="CORRECT.LP", run_dir="/home/XXXX/XDSME_TEST/xdsme_TEST", verbose=1)
    res2=tanh_fit(res.vector,res.CChalf)
    EstimateCC_NewHighRes(0.30, res2[0], res2[1], res.CChalf)
