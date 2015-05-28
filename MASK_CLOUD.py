import gdal
from gdalconst import *
import numpy as np
import numpy.ma as ma
import time as tm
import os
import sys

def setcwd():
    
    cwd = os.getcwd()
    return cwd

def findFmask(cwd):
    
    listdir = os.listdir(cwd)
    fn = None
    for f in listdir:
        if '_MTLFmask.hdr' in f:
            pass
        elif '_MTLFmask' in f:
            fn = f

    if fn == None:
        print 'Cannot find Fmask output.'
        sys.exit(1)
    else:
        print 'Found: ' + fn
        return fn

def modName(nom):

    fn = nom.strip().split('.TIF')
    return fn[0]+'_CMSK.TIF'

def cloudmask(cloud, cwd):

    tifList = []
    listdir = os.listdir(cwd)
    
    for f in listdir:
        if '.TIF' in f:
            tifList.append(f)
        else:
            pass
        
    print tifList
    
    if len(tifList) == 0:
        print 'Cannot find tif images.'
        sys.exit(1)
    
    cloudClass = gdal.Open(cloud, GA_ReadOnly)
    cloudBand = cloudClass.GetRasterBand(1)

    #iterate by every tif image in directory
    for i in tifList:
        landsatImg = gdal.Open(i, GA_ReadOnly)

        if landsatImg == None:
            print 'Cannot find Landsat Image.'
            sys.exit(1)

        #retrieve image attributes
        cols, rows = landsatImg.RasterXSize, landsatImg.RasterYSize
        proj, geotrans = landsatImg.GetProjection(), landsatImg.GetGeoTransform()
        driver = landsatImg.GetDriver()

        #retrieve bands
        landsatBand = landsatImg.GetRasterBand(1)
        
        #create output data set
        output = driver.Create(modName(i), cols, rows, 1,GDT_Float32)
        output.SetGeoTransform(geotrans)
        output.SetProjection(proj)
        outband = output.GetRasterBand(1)

        #iterate through blocks
        xbs = 500
        ybs = 500

        for i in range(0,rows,ybs):
            if rows>i+ybs:
                numrows = ybs
            else:
                numrows = rows-i
            for j in range(0,cols,xbs):
                if cols>j+xbs:
                    numcols = xbs
                else:
                    numcols = cols-j
                landsatArray = landsatBand.ReadAsArray(j,i,numcols,numrows)
                cloudArray = cloudBand.ReadAsArray(j,i,numcols,numrows)
                   
                #use numpy functions to create mask of cloud and cloud shadows
                mask = np.where((cloudArray==2)+(cloudArray==4),0,1)
                img = mask*landsatArray
                outband.WriteArray(img,j,i)

        #save band data
        outband.FlushCache()

        #clear memory for next img iteration
        landsatImg = None
        landsatBand = None
        landsatArray = None
        cloudArray = None
        maskshadow = None
        maskcloud = None
        mask = None
        img = None
        output = None
        outBand = None
        
    #clear cloud class data after iteration
    cloudClass = None
    cloudBand = None
    
def main():

    start = tm.time()
    print 'Preparing mask...'

    cworkdir = setcwd()
    fmaskoput = findFmask(cworkdir)
    cloudmask(fmaskoput, cworkdir)

    print 'Process time: %f' % (tm.time()-start)

if __name__=='__main__':
    main()
