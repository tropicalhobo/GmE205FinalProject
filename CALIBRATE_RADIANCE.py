import os
import gdal
from gdalconst import *
import numpy as np
import time
import sys

def setcwd():
    
    cwd = os.getcwd()
    return cwd

def findMTL(cwd):
    """Finds and metadata file and returns its name string."""
    listdir = os.listdir(cwd)
    fn = None
    for f in listdir:
        if '_MTL.txt' in f:
            fn = f

    if fn == None:
        print 'Cannot find metadata file.'
        sys.exit(1)
    else:
        return fn

def modifyName(nom):
    """Returns modified input file name string."""
    fn = nom.strip().split('.TIF')
    return fn[0]+'_CALIBRATED.TIF'

def collectValues(cwd):
    """Reads metadata txt file and retrieves and then returns a list of calibrateRadiance values."""
    mtl = findMTL(cwd)
    openMTL = open(mtl, 'r')
    rescaleValues = {} 
    start = False
    #Collect calibrateRadiance values from metadata file
    for i in openMTL:
        if 'GROUP = RADIOMETRIC_RESCALING' in i: 
            start = True
        elif start:
            if 'RADIANCE' in i:
                a = i.strip().split('=')
                rescaleValues[a[0].strip()] = float(a[1].strip())            
        if ' END_GROUP = RADIOMETRIC_RESCALING' in i:
            break
    openMTL.close()
    return rescaleValues

def sortValues(d):  
    """Returns a tuple of list of sorted key values."""
    mult = {}
    add = {}
    thermAdd = {}
    therMult = {}
    #Sort between multiply and add constants.
    #Thermal bands for Landsat 7 and 8 are isolated because they disrupt sorted key values.
    for i in d:
        if 'ADD_BAND_10' in i:   
            thermAdd[i] = d[i]
        elif 'ADD_BAND_11' in i: 
            thermAdd[i] = d[i]
        elif 'MULT_BAND_10' in i:
            therMult[i] = d[i]
        elif 'MULT_BAND_11' in i:
            therMult[i] = d[i]
        elif 'MULT_BAND_8' in i:
            pass
        elif 'ADD_BAND_8' in i:
            pass
        elif 'ADD_BAND_6_VCID_1' in i:   
            thermAdd[i] = d[i]
        elif 'ADD_BAND_6_VCID_2' in i:
            thermAdd[i] = d[i]
        elif 'MULT_BAND_6_VCID_1' in i:
            therMult[i] = d[i]
        elif 'MULT_BAND_6_VCID_2' in i:
            therMult[i] = d[i]
        elif 'MULT' in i:
            mult[i] = d[i]
        else:
            add[i] = d[i]
    tup = sorted(mult), sorted(add), sorted(thermAdd), sorted(therMult)
    return tup
    #print sorted(mult), '\n', sorted(add),'\n', sorted(thermAdd),'\n', sorted(therMult)

def calibrateRadiance(cwd):
    """Opens raw .TIF images and applies radiometric calibrateRadiance constants."""
    tifList = []
    thermList = []
    resValue = collectValues(cwd)
    tups = sortValues(resValue)
    dirlist = os.listdir(cwd)
    
    for f in dirlist:
        if 'B10_CMSK' in f:
            thermList.append(f)
        elif 'B11_CMSK' in f: 
            thermList.append(f)
        elif 'B8_CMSK' in f: #ignore panchromatic for Landsat 7 and 8
            pass
        elif 'VCID_1_CMSK' in f:
            thermList.append(f)
        elif 'VCID_2_CMSK' in f:
            thermList.append(f)
        elif '_CMSK.TIF' in f:
            tifList.append(f)

    for i,j,k in zip(tifList,tups[0],tups[1]):
        ds = gdal.Open(i, GA_ReadOnly)
        cols = ds.RasterXSize
        rows = ds.RasterYSize
        bands = ds.RasterCount
        geotrans = ds.GetGeoTransform()
        projection = ds.GetProjection()
        driver = ds.GetDriver()
        
        print i, j, k
        print "Columns: %d\nRows: %d\nBands: %d" % (rows, cols, bands)
        data = ds.ReadAsArray(0,0,cols,rows).astype('float32')
        
        rArray = resValue[j]*data+resValue[k]
      
        oDs = driver.Create(modifyName(i),cols,rows,1, GDT_Float32)
        oDs.SetProjection(projection)
        oDs.SetGeoTransform(geotrans)
        oBand = oDs.GetRasterBand(1)
        oBand.WriteArray(rArray, 0, 0)
        oBand.FlushCache()
        
        ds = None
        data = None
        oDs = None

    calibrateThermal(thermList, tups[2], tups[3], resValue)

def calibrateThermal(band, tAdd, tMult, resMain):
    """calibrateRadiances Landsat 7 and 8 thermal bands."""
    for l, m, n in zip(band, tAdd, tMult):  
        ds = gdal.Open(l, GA_ReadOnly)
        cols = ds.RasterXSize
        rows = ds.RasterYSize
        bands = ds.RasterCount
        geotrans = ds.GetGeoTransform()
        projection = ds.GetProjection()
        driver = ds.GetDriver()
        
        print l, m, n
        print "Columns: %d\nRows: %d\nBands: %d" % (rows, cols, bands)
        data = ds.ReadAsArray(0,0,cols,rows).astype('float32')
        
        rArray = resMain[m]*data+resMain[n]
      
        oDs = driver.Create(modifyName(l),cols,rows,1, GDT_Float32)
        oDs.SetProjection(projection)
        oDs.SetGeoTransform(geotrans)
        oBand = oDs.GetRasterBand(1)
        oBand.WriteArray(rArray, 0, 0)
        oBand.FlushCache()
        
        ds = None
        data = None
        oDs = None
            
def main():
    start = time.time()
    workdir = setcwd()
    
    calibrateRadiance(workdir)

    print time.time()-start, 'seconds'
    
if __name__=='__main__':
    main()
