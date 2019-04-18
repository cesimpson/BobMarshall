# -*- coding: utf-8 -*-
"""
Created on Wed Feb  6 12:37:51 2019

@author: utgstc1training
"""
import arcpy
from arcpy.sa import *
import os
import gdal

#arcpy.env.workspace = r'\\166.2.126.25\teui1\4_Claire\BobMarshall\Data\Vector\WaterMask'
arcpy.env.overwriteOutput=True

#Take water polygons and turn them into a raster water mask

def clipAndAlign(tif,shp,outputName,ndval='-9999'):
    # Replace a layer/table view name with a path to a dataset (which can be a layer file) or 
    #create the layer/table view within the script
    # The following inputs are layers or table views: "Topography_BM_Mosaic_ResetProp_3clip_fill10m.tif", 
    #"MT_NAIP_10m_BMROI.tif"
    arcpy.Clip_management(in_raster=tif,\
                          rectangle="254025 5194145 398555 5393615", \
                          out_raster=r'\\166.2.126.25\teui1\4_Claire\BobMarshall\Data\Vector\temp1234.tif', \
                          in_template_dataset= template, \
                          nodata_value=ndval, \
                          clipping_geometry="NONE", \
                          maintain_clipping_extent="MAINTAIN_EXTENT")
    
   
    arcpy.Clip_management(in_raster=r"\\166.2.126.25\teui1\4_Claire\BobMarshall\Data\Vector\temp1234.tif", \
                          rectangle="254028.020127131 5194146.28504094 398554.37605544 5393611.18447183", \
                          out_raster=outputName, \
                          in_template_dataset=shp, \
                          nodata_value=ndval, \
                          clipping_geometry="ClippingGeometry", \
                          maintain_clipping_extent="NO_MAINTAIN_EXTENT")
    try:
        arcpy.Delete_management(r"\\166.2.126.25\teui1\4_Claire\BobMarshall\Data\Vector\temp1234.tif")
    except:
        print ("could not delete temporary raster (temp1234.tif') from workspace")


WaterShp = r'\\166.2.126.25\teui1\4_Claire\BobMarshall\Data\Vector\WaterMask\WaterMask_NHD_NAIPClass_ManualV3.shp'
print (gdal.Info(WaterShp))
template = os.path.join(r'\\166.2.126.25\teui1\4_Claire\BobMarshall\Data\Raster\MT_NAIP\MT_NAIP_BMROI','MT_NAIP_10m_BMROI.tif')
outWaterMask = WaterShp.replace('.shp', '_ras.tif')
filePath = r'C:\Users\clairesimpson\Downloads'
clippingShp = os.path.join(filePath, 'BM_AOI_reproj.shp')
#convert polygon shp to raster
arcpy.PolygonToRaster_conversion(WaterShp, 'FIDnum', outWaterMask, 'CELL_CENTER', '#', template)
clipAndAlign(outWaterMask, clippingShp, outWaterMask.replace('.tif', '_pixAlign.tif'))
arcpy.Delete_management(outWaterMask)
# Replace a layer/table view name with a path to a dataset (which can be a layer file) or create the layer/table view within the script
# The following inputs are layers or table views: "WaterMask_NHD_NAIPClass_ManualV2_pixAlign.tif"

# Replace a layer/table view name with a path to a dataset (which can be a layer file) or create the layer/table view within the script
# The following inputs are layers or table views: "WaterMask_NEDLS.tif"

print ('done with shp polys to raster mask for water masking')
#clip and align polygon to NAIP imagery