import gdal
from gdalconst import *
import numpy as np
import numpy.ma as ma
import time as tm

print 'Preparing mask...'

#open datasources
start = tm.time()
fN = 'LC81110552013256LGN00_B1_CALIBRATED.TIF'
fN2 = 'LC81110552013256LGN00_MTLFmask'

landsatImg = gdal.Open(fN, GA_ReadOnly)
cloudClass = gdal.Open(fN2, GA_ReadOnly)

if landsatImg == None:
    print 'Cannot find Landsat Image.'
    
if cloudClass == None:
    print 'Cannot find Fmask output.'

#retrieve image attributes
cols, rows = landsatImg.RasterXSize, landsatImg.RasterYSize
proj, geotrans = landsatImg.GetProjection(), landsatImg.GetGeoTransform()
driver = cloudClass.GetDriver()

#retrieve bands
landsatBand = landsatImg.GetRasterBand(1)
cloudBand = cloudClass.GetRasterBand(1)

#create output data set
output = driver.Create('Masked.TIF', cols, rows, 1,GDT_Float32)
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

#manage memory
landsatImg = None
cloudClass = None
landsatBand = None
cloudBand = None
landsatArray = None
cloudArray = None
maskshadow = None
maskcloud = None
mask = None
img = None
output = None
outBand = None

print 'Process time: %f' % (tm.time()-start)
