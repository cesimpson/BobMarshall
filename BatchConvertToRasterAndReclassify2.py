# -*- coding: utf-8 -*-
"""
Created on Mon Apr  8 17:54:16 2019

@author: clairesimpson
"""

# convert NHD streamfiles to raster mosaic 
# project to same prj as clip shp;
# clip to boundary
# convert polyline to raster
# mosaic rasters together

import arcpy
import os
from arcpy.sa import *
arcpy.CheckOutExtension('Spatial')

fileForProj = r'\\166.2.126.25\teui1\4_Claire\BobMarshall\Data\Raster\LayerGroupsForcLHA\10mInt\NotClippedToTrailBuf\DEF_30m_wgs_tps_predict_v2_ResetProp_3clipInt.tif'
arcpy.env.snapRaster =Raster(fileForProj)

fp = r'F:\BMShareDrive\Montana NHD\NHD_H_Montana_State_Shape\Shape\Streams_'
clipShp = r'\\166.2.126.25\teui1\4_Claire\BobMarshall\Data\Vector\BM_AOI\LargeBm_AOI\LargeBM_AOI.shp'
arcpy.env.workspace = fp
arcpy.env.overwriteOutput = True
outcoor="PROJCS['NAD_1983_UTM_Zone_12N',GEOGCS['GCS_North_American_1983',DATUM['D_North_American_1983',SPHEROID['GRS_1980',6378137.0,298.257222101]],PRIMEM['Greenwich',0.0],UNIT['Degree',0.0174532925199433]],PROJECTION['Transverse_Mercator'],PARAMETER['False_Easting',500000.0],PARAMETER['False_Northing',0.0],PARAMETER['Central_Meridian',-111.0],PARAMETER['Scale_Factor',0.9996],PARAMETER['Latitude_Of_Origin',0.0],UNIT['Meter',1.0]]"   

for f in os.listdir(fp):
    if f.endswith('prj.shp'):# and ('6' in f):
        print (f)
        outprj=f
        #outprj = f.replace('.shp', 'prj.shp')
        outname = f.replace('.shp', '_ras.tif')
        outclip = f.replace('.shp', 'clip.shp')
        print ('projecting')
        #outprj =arcpy.Project_management(f, outprj, outcoor)
        
        arcpy.Clip_analysis (outprj, clipShp, outclip)
        print ('converting to ras:',outclip)

        arcpy.PolylineToRaster_conversion(outclip, 'FID', outname, '','',10)
        
        
rasList = []

for ras in os.listdir(fp):
    if ras.endswith('prj_ras.tif'):
        rasList.append(os.path.join(fp,ras))

for i in rasList:
    print (i)
#rasList = [r'F:\BMShareDrive\Montana NHD\NHD_H_Montana_State_Shape\Shape\Streams_\NHDFlowline5_ras.tif',
#           r'F:\BMShareDrive\Montana NHD\NHD_H_Montana_State_Shape\Shape\Streams_\NHDFlowline6_ras.tif',
#           r'F:\BMShareDrive\Montana NHD\NHD_H_Montana_State_Shape\Shape\Streams_\streamMosaic1.tif']
#       
arcpy.MosaicToNewRaster_management(rasList, fp, 'streamMosaic3.tif','','32_BIT_UNSIGNED',10, 1,'MAXIMUM','FIRST')


print ('done')