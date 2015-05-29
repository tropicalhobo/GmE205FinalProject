import gdal
from gdalconst import *
import numpy as np
import os, sys, time
from math import sqrt

def setcwd():
    """Sets current working directory of the script."""
    cwd = os.getcwd()
    return cwd

def modifyName(nom):
    """Returns modified input file name string."""
    fn = nom.strip().split('.TIF')
    return fn[0] + '_NDBI.TIF'

def transformNDBI(cwd):
    """Transform Landat dataset to NDBI."""
   
    band4 = None
    band5 = None
    fName = ''
    workspace = os.listdir(cwd)
    
    for f in workspace:
        
        if 'B4_CMSK_REFLECTANCE.TIF' in f: 
            band4 = gdal.Open(f, GA_ReadOnly)
            fName = f
            print f
        elif 'B5_CMSK_REFLECTANCE.TIF' in f:
            band5 = gdal.Open(f, GA_ReadOnly)
            print f

    if band4 == None or band5 == None:
        print 'Cannot find images.'
        sys.exit(1)
    else:
        pass
           
    b4cols, b4rows = band4.RasterXSize, band4.RasterYSize
    b5cols, b5rows = band5.RasterXSize, band5.RasterYSize
    geotrans, proj = band5.GetGeoTransform(), band5.GetProjection()
    driver = band5.GetDriver()
        
    data4 = band4.ReadAsArray(0,0,b4cols,b4rows).astype('float32')
    data5 = band5.ReadAsArray(0,0,b5cols,b5rows).astype('float32')
    
    ndbi = (data5-data4)/(data4+data5)
     
    outData = driver.Create(modifyName(fName),b5cols,b5rows,1, GDT_Float32)
    outData.SetProjection(proj)
    outData.SetGeoTransform(geotrans)
    oBand = outData.GetRasterBand(1)
    oBand.WriteArray(ndbi)
    oBand.FlushCache()

    #Memory management    
    band4 = None
    band5 = None
    
    data4 = None
    data5 = None

    ndbi = None
    
    outData = None

def main():
    start = time.time()

    cwd = setcwd()
    transformNDBI(cwd)
    
    print time.time()-start, 'seconds'
    
if __name__=='__main__':
    main()
