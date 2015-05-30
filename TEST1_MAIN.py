import gdal
from gdalconst import *
import os, sys
import time as tm
import MASK_CLOUD as mc
import CALIBRATE_RADIANCE as crad
import CALIBRATE_REFLECTANCE as cref
import TRANSFORM_NDBI as tn

def main():
    start = tm.time()
    
    workdir = mc.setcwd()
    fmaskout = mc.findFmask(workdir)
    mc.cloudmask(fmaskout,workdir)
    #calibrate
    crad.calibrateRadiance(workdir)
    cref.calibrateReflectance(workdir)
    #tn.transformNDBI(workdir)

    print 'Script process took %f seconds' % (tm.time()-start)
    
if __name__=='__main__':
    main()
