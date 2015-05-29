import os
import gdal
from gdalconst import *
import numpy as np
import time
from math import pi, sin
import sys

def setcwd():
    """Sets current working directory of the script."""
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

def findDistance(cwd):
    """Finds the text file containing
    AU distance between sun and earth
    on a particular DOY."""
    fn = None
    workdir = os.listdir(cwd)
    for f in workdir:
        if 'EARTH-SUN_DISTANCE_AU.txt' in f:
            fn = f
        else:
            pass

    if fn == None:
        print 'Cannot find earth-sun distance txt file.'
        sys.exit(1)
    else:
        return fn

def earthSunDist(txtfile, doy):
    """Retrieves AU distance between sun and earth
    for a particular DOY."""
    txt = open(txtfile,'r')
    distance = 0
    for i in txt:
        if doy in i:
            line = i.strip().split('\t')
            distance = float(line[1])
        else:
            'Cannot find date of year.'
    txt.close()
    return distance
    
def retrieveDOY(fN):
    """Retrieves DOY from the name string
    of a Landsat image file."""
    s = fN.strip().split('_')
    return s[0][13:16]
               
def collectSunElev(f):
    """Collects sun elevation from the image metadata file."""
    txt = open(f, 'r')
    for i in txt:
        if 'SUN_ELEVATION' in i:
            value = i.strip().split('=')
            return (pi/180)*float(value[1])
        else:
            pass
    close.txt()

def modifyName(nom):
    """Returns modified input file name string."""
    fn = nom.strip().split('_RADIANCE.TIF')
    return fn[0]+'_REFLECTANCE.TIF'

def calibrateReflectance(cwd):
    """Calibrates radiance image to reflectance."""
    caList = []
    mtl = findMTL(cwd)
    distfile = findDistance(cwd)
    dist = earthSunDist(distfile,retrieveDOY(mtl))
    sunelev = collectSunElev(mtl)
    eSun = {1:1997,2:1812,3:1533,4:1039,5:230.8,7:84.90,8:1362}
    workspace = os.listdir(cwd)
    
    for i in workspace:
        #ignore thermal bands for all Landsats
        if 'B10_CMSK_RADIANCE' in i:
            pass
        elif 'B11_CMSK_RADIANCE' in i:
            pass
        elif 'VCID_1_CMSK_RADIANCE' in i:
            pass
        elif 'VCID_2_CMSK_RADIANCE' in i:
            pass
        elif 'B6_CMSK_RADIANCE' in i:
            pass
        elif 'CMSK_RADIANCE' in i:
            caList.append(i)

    for j,k in zip(caList,sorted(eSun)):
        print 'Calibrating ' + j + ' to Reflectance.'
        ds = gdal.Open(j, GA_ReadOnly)
        cols, rows = ds.RasterXSize, ds.RasterYSize
        geotrans, proj = ds.GetGeoTransform(), ds.GetProjection()
        driver = ds.GetDriver()

        data = ds.ReadAsArray(0,0,cols,rows)
        reflectance = (pi*data*dist**2)/(eSun[k]*sin(sunelev))

        output = driver.Create(modifyName(j),cols,rows,1,GDT_Float32)
        band = output.GetRasterBand(1)
        band.WriteArray(reflectance)
        band.FlushCache()
        ds = None
        output = None
        band = None
              
def main():
    start = time.time()
   
    sunElevation = collectSunElev(mtl)
    doy = retrieveDOY(mtl)
    distance = earthSunDist(ersun, doy)
    print 'Sun elevation: %s\nDay of year: %s\nDistance: %s' % (
        sunElevation, doy, distance)
    calibrateReflectance(wSpace,distance,sunElevation)
 
    print 'Script run time: %f' % (time.time()-start)
    
if __name__=='__main__':
    main()
