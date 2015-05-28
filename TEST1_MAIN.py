import gdal
from gdalconst import *
import os
import time
import sys
import MASK_CLOUD as mc
import CALIBRATE_RADIANCE as cr

def main():
    workdir = mc.setcwd()
    fmaskout = mc.findFmask(workdir)
    mc.cloudmask(fmaskout,workdir)
    #calibrate
    cr.calibrateRadiance(workdir)
    
if __name__=='__main__':
    main()
