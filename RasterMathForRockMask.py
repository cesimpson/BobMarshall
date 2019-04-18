# -*- coding: utf-8 -*-
"""
Created on Wed Feb  6 13:56:18 2019

@author: utgstc1training
"""

import gdal, osr
import numpy as np
import os
from timeit import default_timer as timer
start = timer()

convertToShp = False

PyLib = r'\\166.2.126.25\teui1\4_Claire\BobMarshall\PythonScripts'

#from (os.path.join(PyLib, 'ResetRasterProperties_10mEPSG29612IntExt.py')) import *
from ResetRasterProperties_10mEPSG29612IntExt import find_elapsed_time
#from train_apply_RandomForests__csv_Wooten import array_to_tif

##############################

filePath = r'\\166.2.126.25\teui1\4_Claire\BobMarshall\Data\Raster\MT_NAIP\MT_NAIP_BMROI\Classifications\MiniBatchKMeans_wIndices'
NDVI = os.path.join(filePath, 'MT_NAIP_10m_BMROINDVI.tif')
NAIP_classification = os.path.join(filePath, 'MT_NAIP_10m_BMROIunsupClass3_rock.tif')
Water = os.path.join(r'\\166.2.126.25\teui1\4_Claire\BobMarshall\Data\Vector\WaterMask', 'WaterMask_NHD_NAIPClass_ManualV2_pixAlign.tif')

###############################
"""Function to write final classification to tiff"""
def array_to_tif(inarr, outfile, imgProperties):

    # get properties from input
    (gt, proj, ncols, nrows, ndval) = imgProperties
    print (ndval)

    drv = drvtif.Create(outfile, ncols, nrows, 1, 3, options = [ 'COMPRESS=LZW' ]) # 1= number of bands (i think) and 3 = Data Type (16 bit signed)
    drv.SetGeoTransform(gt)
    drv.SetProjection(proj)
    drv.GetRasterBand(1).SetNoDataValue(ndval)
    drv.GetRasterBand(1).WriteArray(inarr)

    return outfile

def getProp(VHRstack):
    img_ds = gdal.Open(VHRstack, gdal.GA_ReadOnly) # GDAL dataset
    gt = img_ds.GetGeoTransform()
    proj = img_ds.GetProjection()
    ncols = img_ds.RasterXSize
    nrows = img_ds.RasterYSize
    ndval = img_ds.GetRasterBand(1).GetNoDataValue() # should be -999 for all layers, unless using scene as input
    imgProperties = (gt, proj, ncols, nrows, ndval)
    return imgProperties

################################
gdal.UseExceptions()

drvtif = gdal.GetDriverByName('GTiff')

imgProperties = getProp(NAIP_classification)

NAIP_classification_file = gdal.Open(NAIP_classification,gdal.GA_ReadOnly)
NDVI_file = gdal.Open(NDVI, gdal.GA_ReadOnly)
Water_file = gdal.Open(Water, gdal.GA_ReadOnly)

NAIP_B = NAIP_classification_file.GetRasterBand(1)
NAIP_Array = NAIP_B.ReadAsArray()
NAIP_shape =  NAIP_Array.shape
print( NAIP_Array)

NDVI_B = NDVI_file.GetRasterBand(1)
NDVI_Array = NDVI_B.ReadAsArray()
NDVI_shape =  NDVI_Array.shape

Water_B = Water_file.GetRasterBand(1)
Water_Array = Water_B.ReadAsArray()
Water_shape = Water_Array.shape

#if pixel is water or area is vegetated.. reclassify t as -9999 nodata val in NAIP classification mask
maskOut = np.logical_or(Water_Array == 0, NDVI_Array > 0 ) #areas to exclude 
#water = 0 means water is there; NDVI > 0 means area is vegetated (adjust this param)

NAIP_Array[maskOut] = -9999
print (NAIP_Array)
rockMask = NAIP_Array

#inarr, outfile, imgProperties; returns outfile
outFileName = NAIP_classification.replace('.tif', 'Mask.tif')
outTif = array_to_tif(rockMask, outFileName, imgProperties)
print ("outTif:", outTif)

if convertToShp: #convert to shp for easier manual editting/removal of non-rock regions
    import arcpy
    arcpy.RasterToPolygon_conversion(outTif, outFileName.replace('.tif', '.shp'), "SIMPLIFY") #inraster, outpolys, simplify

elapsed = round(find_elapsed_time(start, timer()),3)
print ("\n\nElapsed time = ",elapsed)