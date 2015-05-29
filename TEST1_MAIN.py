import gdal
from gdalconst import *
import os
import time as tm
import sys
import MASK_CLOUD as mc
import CALIBRATE_RADIANCE as cr
import CALIBRATE_REFLECTANCE as cref

def main():
    start = tm.time()
    
    workdir = mc.setcwd()
    fmaskout = mc.findFmask(workdir)
    mc.cloudmask(fmaskout,workdir)
    #calibrate
    cr.calibrateRadiance(workdir)
    cref.calibrateReflectance(workdir)

    print 'Script process took %f seconds' % (tm.time()-start)
    
if __name__=='__main__':
    main()
