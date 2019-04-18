# -*- coding: utf-8 -*-
"""
Created on Tue Mar 12 14:15:05 2019

@author: clairesimpson
"""

## sample points across grid at interval of xx and convert to shp


import arcpy
from arcpy.sa import *
import os

arcpy.overwriteOutput = False
#read in sample raster and convert to shp
fp = r'\\166.2.126.25\teui1\4_Claire\BobMarshall\Data\Raster\LayerGroupsForcLHA\10mInt\NewWild_TrailsExt'
arcpy.env.workspace = fp
cost = r'\\166.2.126.25\teui1\4_Claire\BobMarshall\Data\Vector\R1_Trails_subset\TrailsCost_5c3_10m4.tif'

xx = 3
createFull = False

if createFull:
    arcpy.RasterToPoint_conversion(cost,'SampleGrid_full.shp')
    
FullPoints = 'SampleGrid_full.shp'
arcpy.CopyFeatures_management(FullPoints, FullPoints.replace('full.shp','copy{}0m.shp'.format(xx)))
PointShp = FullPoints.replace('full.shp','copy{}0m.shp'.format(xx))
    

#extract values from other rasters to point shp
rasList = [f for f in os.listdir(fp) if (f.endswith('.tif'))]
rasList.append(cost)
print (rasList)



#delete every xx row e.g. every 3rd row (FID%xx ==0)
with arcpy.da.UpdateCursor(PointShp, ['FID', 'gridcode']) as cursor:
    naVal = cursor[0][1]
    print('na val is:',naVal)
    for row in cursor:
        if row[0]%xx != 0 or (row[1] == 'NoData' or row[1]==naVal):
            cursor.deleteRow()

for tif in rasList:
    ExtractMultiValuesToPoints(PointShp,tif)


#arcpy.DeleteField_management(PointShp, 'gridcode')




