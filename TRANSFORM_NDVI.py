import os
import gdal
from gdalconst import *
import numpy as np
import time

def transformNDVI(wrksp):
    """Opens raw .TIF images and applies radiometric rescale constants."""
    band3 = None
    band4 = None
    fName = ''
    for f in wrksp:
        if 'B3' in f:
            band3 = gdal.Open(f, GA_ReadOnly)
            fName = f
            print f
        elif 'B4' in f: 
            band4 = gdal.Open(f, GA_ReadOnly)
            print f
                   
    b3cols = band3.RasterXSize
    b3rows = band3.RasterYSize
    b4cols = band4.RasterXSize
    b4rows = band4.RasterYSize
    geotrans = band3.GetGeoTransform()
    projection = band3.GetProjection()
    driver = band3.GetDriver()
        
    data3 = band3.ReadAsArray(0,0,b3cols,b3rows).astype('float32')
    data4 = band4.ReadAsArray(0,0,b4cols,b4rows).astype('float32')
    #mask = np.greater(data3+data4, 0)
        
    #ndvi = np.choose(mask, (-99, (data4-data3)/(data3+data4)))

    ndvi = (data4-data3)/(data3+data4+0.00000000001)
     
    outData = driver.Create(modifyName(fName),b3cols,b3rows,1, GDT_Float32)
    outData.SetProjection(projection)
    outData.SetGeoTransform(geotrans)
    oBand = outData.GetRasterBand(1)
    oBand.WriteArray(ndvi)
    oBand.FlushCache()
        
    band3 = None
    band4 = None
    data3 = None
    data4 = None
    outData = None

def modifyName(nom):
    """Returns modified input file name string."""
    fn = nom.strip().split('_')
    fn[1] = '_NDVI.TIF'
    return fn[0]+fn[1]

def main():
    start = time.time()

    dire = os.listdir()
    workSpace = os.listdir('C:\\Users\G Torres\\Desktop\\GEOG 213 DATA PROCESSING\\1988081')
    transformNDVI(workSpace)
    
    print time.time()-start, 'seconds'
    
if __name__=='__main__':
    main()
