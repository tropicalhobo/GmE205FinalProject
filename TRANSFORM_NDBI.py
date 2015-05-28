import os
import gdal
from gdalconst import *
import numpy as np
import time
from math import sqrt

def transformNDBI(wrksp):
    """Opens raw .TIF images and applies radiometric rescale constants."""
   
    band4 = None
    band5 = None
    fName = ''
    for f in wrksp:
        
        if 'B4' in f: 
            band4 = gdal.Open(f, GA_ReadOnly)
            fName = f
            print f
        elif 'B5' in f:
            band5 = gdal.Open(f, GA_ReadOnly)
            print f 
           
    b4cols = band4.RasterXSize
    b4rows = band4.RasterYSize
    b5cols = band5.RasterXSize
    b5rows = band5.RasterYSize
    geotrans = band5.GetGeoTransform()
    projection = band5.GetProjection()
    driver = band5.GetDriver()
        
    data4 = band4.ReadAsArray(0,0,b4cols,b4rows).astype('float32')
    data5 = band5.ReadAsArray(0,0,b5cols,b5rows).astype('float32')
    
    ndbi = (data5-data4)/(data4+data5)
     
    outData = driver.Create(modifyName(fName),b5cols,b5rows,1, GDT_Float32)
    outData.SetProjection(projection)
    outData.SetGeoTransform(geotrans)
    oBand = outData.GetRasterBand(1)
    oBand.WriteArray(ndbi)
    oBand.FlushCache()
        
    band4 = None
    band5 = None
    
    data4 = None
    data5 = None
    
    outData = None

def modifyName(nom):
    """Returns modified input file name string."""
    fn = nom.strip().split('_')
    fn[1] = '_NDBI.TIF'
    return fn[0]+fn[1]

def main():
    start = time.time()

    workSpace = os.listdir('C:\\Users\G Torres\\Desktop\\GEOG 213 DATA PROCESSING\\1988081')
    transformNDBI(workSpace)
    
    print time.time()-start, 'seconds'
    
if __name__=='__main__':
    main()
