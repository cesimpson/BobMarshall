# -*- coding: utf-8 -*-
"""
Created on Thu Mar  7 13:17:28 2019

@author: clairesimpson
"""
import arcpy
import gdal, osr, ogr
import os
from timeit import default_timer as timer


#allow verbose error reporting
gdal.UseExceptions()
arcpy.env.workspace = r'C:\Users\clairesimpson\Downloads'
#r'\\166.2.126.25\teui1\4_Claire\BobMarshall\Data\Raster\Climate\ZackClimate_Processed_Updated'
#^ where temp tif file will be located (and deleted from..)
#specify file path
filePath = r'\\166.2.126.25\teui1\4_Claire\BobMarshall\Data\Vector\BM_AOI'
clippingShp = os.path.join(filePath, 'BM_AOI_reproj.shp')
out_coor_system1="PROJCS['NAD_1983_UTM_Zone_12N',GEOGCS['GCS_North_American_1983',DATUM['D_North_American_1983',SPHEROID['GRS_1980',6378137.0,298.257222101]],PRIMEM['Greenwich',0.0],UNIT['Degree',0.0174532925199433]],PROJECTION['Transverse_Mercator'],PARAMETER['False_Easting',500000.0],PARAMETER['False_Northing',0.0],PARAMETER['Central_Meridian',-111.0],PARAMETER['Scale_Factor',0.9996],PARAMETER['Latitude_Of_Origin',0.0],UNIT['Meter',1.0]]"   
arcpy.env.overwriteOutput=True                        
arcpy.env.snapRaster()
fileForProj = os.path.join(r'\\166.2.126.25\teui1\4_Claire\BobMarshall\Data\Raster\MT_NAIP\MT_NAIP_BMROI','MT_NAIP_30m_BMROI.tif')

def clipAndAlign(tif,shp,outputName,ndval='-9999'):
    # Replace a layer/table view name with a path to a dataset (which can be a layer file) or 
    #create the layer/table view within the script
    # The following inputs are layers or table views: "Topography_BM_Mosaic_ResetProp_3clip_fill10m.tif", 
    #"MT_NAIP_10m_BMROI.tif"
    arcpy.Clip_management(in_raster=tif,\
                          rectangle="254025 5194145 398555 5393615", \
                          out_raster='temp12345.tif', \
                          in_template_dataset=fileForProj, \
                          nodata_value=-9999, \
                          clipping_geometry="NONE", \
                          maintain_clipping_extent="MAINTAIN_EXTENT")
    # Replace a layer/table view name with a path to a dataset (which can be a layer file) or 
    #create the layer/table view within the script
    # The following inputs are layers or table views: "Elevation_clip.tif"
    arcpy.Clip_management(in_raster="temp12345.tif", \
                          rectangle="254028.020127131 5194146.28504094 398554.37605544 5393611.18447183", \
                          out_raster=outputName, \
                          in_template_dataset=shp, \
                          nodata_value=ndval, \
                          clipping_geometry="ClippingGeometry", \
                          maintain_clipping_extent="NO_MAINTAIN_EXTENT")
    try:
        arcpy.Delete_management('temp1234.tif')
    except:
        print ("could not delete temporary raster (temp1234.tif') from workspace")


folder = r'\\166.2.126.25\teui1\4_Claire\BobMarshall\Data\Raster\Climate\ZackClimate'
for f in os.listdir(folder):
    if f.endswith('.tif') and ('tmin' in f) and ('prj' not in f):
        print (f)
        tif = os.path.join(folder, f)
        arcpy.ProjectRaster_management(tif,tif.replace('.tif','prj.tif'),out_coor_system1)
        
        clipAndAlign(tif.replace('.tif','prj.tif'), clippingShp,tif.replace('.tif','prjClip.tif'))
        arcpy.Resample_management (tif.replace('.tif','prjClip.tif'), tif.replace('.tif','prjClipResam.tif'), '30', 'BILINEAR')
        
        
        
        
        
        