# -*- coding: utf-8 -*-
"""
Created on Fri Feb  1 10:22:34 2019

@author: utgstc1training
"""

import arcpy
from arcpy.sa import *
import gdal
import os
from timeit import default_timer as timer


gdal.UseExceptions()

arcpy.CheckOutExtension('Spatial')

filePath = r'\\166.2.126.25\teui1\4_Claire\BobMarshall\Data\Raster\MT_NAIP\MT_NAIP_BMROI\Classifications\MiniBatchKMeans_wIndices'
arcpy.env.workspace = filePath

landCover = 'MT_NAIP_10m_BMROIunsupClass3.tif'
TopoRas = r'\\166.2.126.25\teui1\4_Claire\BobMarshall\Data\Raster\Topography\Topography_BM_Mosaic.tif'
Slope =r'\\166.2.126.25\teui1\4_Claire\BobMarshall\Data\Raster\Topography\Slope_clip_pixAlign.tif'
# arcpy.MakeRasterLayer_management(TopoRas, 'slopelyr','#', '#', '2')#gdal.Open(TopoRas, gdal.GA_ReadOnly).GetRasterBand(2)
waterVals = [8,12,15,16,23,29]
thresholdSlope = 5
thresholdArea = 500

testrun = 2
outWaterReclass =landCover.replace('.tif', '_waterReclass'+str(testrun)+'.tif')
deleteIntermediateFiles = False


start = timer()    

def find_elapsed_time(start, end): # example time = round(find_elapsed_time(start, end),3) where start and end = timer()
    elapsed_min = (end-start)/60
    return float(elapsed_min)


def reclassifyWater():
    """ 
    By looking at classification in Arc, decide which classes contain water
    merge these into one class (1) and all other classes into a different class (0)
    """
    remap = []
    nonWater = [i+1 for i in range(30)if i+1 not in waterVals]
    print (nonWater)
    
    for val in waterVals:
        remap.append([val,100])
    for val in nonWater:
        remap.append([val, 200])
    
    print ('\n',remap)
    
    outReclass = arcpy.sa.Reclassify(landCover, "Value",RemapRange(remap))
    #outReclass.save(outWaterReclass)
    return outReclass
outReclass = 'outReclassPoly1_copy.shp'    
def getAvgSlopePerWaterBody(outReclass):
    """
    1. Convert raster reclassification to polygons delineating water
    2. Calculate area of polygons and eliminate polygons under threshold area
    3. Calculate median slope per polygon
    4. If median slope < threshold, polygon is water
    """
    
    #1 Convert water raster to polygons
    #outPolys = arcpy.CopyFeatures_management('outReclassPoly'+str(testrun)+'.shp', 'outReclassPoly'+str(testrun)+'_copy.shp')
    outReclassPolys = 'outReclassPoly'+str(testrun)+'_copy.shp'
    outMedSlopePolys = 'outMedSlopeShp'+str(testrun)+'.shp'
    outMedSlopePoints='outMedSlopePoints'+str(testrun)+'.shp'
    outWaterPolys = 'outWaterPolys'+str(testrun)+'.shp'
    outWaterMask = 'outWaterMask'+str(testrun)+'.tif'
    arcpy.RasterToPolygon_conversion(outReclass, outReclassPolys, "SIMPLIFY") #inraster, outpolys, simplify
    print ("Adding fields")
    #2a Calculate Area Field
    arcpy.AddField_management(outReclassPolys, "Area_m", 'FLOAT')
    #3 Create Field for median slope
    arcpy.AddField_management(outReclassPolys, "MedSlope","FLOAT")
    
    #2b Get area of each polygon and remove nonwater polygons
    with arcpy.da.UpdateCursor(outReclassPolys, ['Area_m', 'SHAPE@AREA', 'gridcode', 'MedSlope']) as cursor:
        for row in cursor:
            if row[2] == 100: #Water
                row[0] = row[1]
                #2c remove water polygons smaller than threshold     
            cursor.updateRow(row)
            if row[1] < thresholdArea or row[2] ==200:
                cursor.deleteRow()
                
           
    
    print ("Calculating zonal stats")   
        
    #3 Calculate median value per water poly
    #zone layer, value layer, 
    statsRas = ZonalStatistics(outReclassPolys, "FID",Slope, "MEDIAN")
    statsRas.save('StatsRas_'+str(testrun)+'.tif')
    print ("Converting statistics raster to polygon")
    #3b Convert raster to polygon shapefile
    arcpy.RasterToPolygon_conversion(statsRas, outMedSlopePolys, "NO_SIMPLIFY") 
    #NB number of med slope polygons will be less than number of out reclass polygons 
    #bc some raster pixels taht were in adjacet polygons will have merged


    #### ARE THESE NEXT 2 STEPS NECESSARY OR CAN WE JUST USE RASTER TO POLYGON SHP?
    print ("Converting polygon shp to point shp")
    #Convert polygon shp to point shp (each point contains the median slope value for the 'water' polygon within
    #which the point is located)
    arcpy.FeatureToPoint_management(outMedSlopePolys, outMedSlopePoints, "INSIDE")
    #where gridcode designates the median slope of the polygon
    
    print("Joining median slope value to water polygons")
    #Join point attribute (med slope) to water polygons
    #target features, join features, out feature class:
    #Attributes of the target features and the attributes from the joined features are transferred to the output feature class.
    arcpy.SpatialJoin_analysis(outReclassPolys, outMedSlopePoints, outWaterPolys)
    
    #AND INSTEAD USE OUTMEDSLOPEPOLYS AS SHP IN CURSOR??
    print ("removing false 'water' polygons from water shp mask")
    with arcpy.da.UpdateCursor(outWaterPolys, ["gridcode"]) as cursor:
        for row in cursor:
            if row[0] > thresholdSlope:
                cursor.deleteRow()
    print ("Converting water polygons to raster")
    arcpy.PolygonToRaster_conversion(outWaterPolys, 'gridcode', outWaterMask)
                                     
    if deleteIntermediateFiles:
        for f in [statsRas,outMedSlopePolys,outMedSlopePoints,outReclassPolys]:
            try:
                arcpy.Delete_management(f)
            except:
                print ("\nFailed to delete:",f)
                          

#output = reclassifyWater()

#getAvgSlopePerWaterBody(outWaterReclass)
          
elapsed = round(find_elapsed_time(start, timer()),3)
print ("\n\nElapsed time = {}".format(elapsed))   
