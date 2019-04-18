# -*- coding: utf-8 -*-
"""
Created on Thu Jan 24 14:02:45 2019

@author: utgstc1training
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

filePath = r'\\166.2.126.25\teui1\4_Claire\BobMarshall\Data\Raster\Climate\PRISM'
#r'\\166.2.126.25\teui1\4_Claire\BobMarshall\Data\Raster\Climate\ZackClimate'
#r'\\166.2.126.25\teui1\4_Claire\BobMarshall\Data\Raster\Topography'


ContainsSubdirs = True #ie if false, files are within filepath directly
#set this to true if you want to process files within subdirectories within the filepath 

toClip = True #set this if want to involve clipping also 


#SET THESE GLOBAL VARS:target projection, target extent, target data type, target spatial resolution

#Target Reference System  #changes from projected to geographic coordinates
"""
EPSG:26912
NAD83 / UTM zone 12N (Google it)

WGS84 Bounds: -114.0000, 24.8300, -108.0000, 79.2500
Projected Bounds: 196765.3486, 2749459.8086, 803234.6514, 8799482.7282
Scope: Large and medium scale topographic mapping and engineering survey.
Last Revised: May 29, 2007
Area: North America - 114°W to 108°W and NAD83 by country
"""
global_tgt_srs1=osr.SpatialReference() 
global_tgt_srs1.ImportFromWkt("""PROJCS["NAD83 / UTM zone 12N",
    GEOGCS["NAD83",
        DATUM["North_American_Datum_1983",
            SPHEROID["GRS 1980",6378137,298.257222101,
                AUTHORITY["EPSG","7019"]],
            AUTHORITY["EPSG","6269"]],
        PRIMEM["Greenwich",0,
            AUTHORITY["EPSG","8901"]],
        UNIT["degree",0.01745329251994328,
            AUTHORITY["EPSG","9122"]],
        AUTHORITY["EPSG","4269"]],
    UNIT["metre",1,
        AUTHORITY["EPSG","9001"]],
    PROJECTION["Transverse_Mercator"],
    PARAMETER["latitude_of_origin",0],
    PARAMETER["central_meridian",-111],
    PARAMETER["scale_factor",0.9996],
    PARAMETER["false_easting",500000],
    PARAMETER["false_northing",0],
    AUTHORITY["EPSG","26912"],
    AXIS["Easting",EAST],
    AXIS["Northing",NORTH]]""")

fileForProj = os.path.join(r'\\166.2.126.25\teui1\4_Claire\BobMarshall\Data\Raster\MT_NAIP\MT_NAIP_BMROI','MT_NAIP_30m_BMROI.tif')

a = gdal.Open(fileForProj)
prj=a.GetProjection()
global_tgt_srs=osr.SpatialReference()
global_tgt_srs.ImportFromWkt(prj) 
print (global_tgt_srs)

    
global_tgt_dt = gdal.GDT_Float32
global_tgt_res = 10 #m                                


def find_elapsed_time(start, end): # example time = round(find_elapsed_time(start, end),3) where start and end = timer()
    elapsed_min = (end-start)/60
    return float(elapsed_min)

def getExtent(gt,cols,rows):
    ''' Return list of corner coordinates from a geotransform

        @type gt:   C{tuple/list}
        @param gt: geotransform
        @type cols:   C{int}
        @param cols: number of columns in the dataset
        @type rows:   C{int}
        @param rows: number of rows in the dataset
        @rtype:    C{[float,...,float]}
        @return:   coordinates of each corner
    '''
    ext=[]
    xarr=[0,cols]
    yarr=[0,rows]

    for px in xarr:
        for py in yarr:
            x=gt[0]+(px*gt[1])+(py*gt[2])
            y=gt[3]+(px*gt[4])+(py*gt[5])
            ext.append([x,y])
            print (x,y)
        yarr.reverse()
    return ext

#############################################################
def getRasterInfo(myFile):
    """ RETURN RASTER PROPERTIES: extent, spatial reference, spatial resolution of raster """
    
    print ('\nstarting: get raster info')
    
    #Open raster file
    ds=gdal.Open(myFile)
    
    #get the geometric tranformation of file
    #returns in order: ulX, xDist(i.e. pixel width), rtnX, ulY, rtnY, yDist(i.e. pixel height)
    gt=ds.GetGeoTransform()
   
    #get number of columns and row in file 
    cols = ds.RasterXSize
    rows = ds.RasterYSize
    
    #extent (is this the same as extent used in clipRasterToShp?)
    ext=getExtent(gt,cols,rows)
    
    #Spatial Reference System of file
    src_srs=osr.SpatialReference()
    src_srs.ImportFromWkt(ds.GetProjection())   
    #pixel size i.e. spatial resolution of file
    x_size = gt[1] 
    y_size = -gt[5]
    
    return ext, src_srs, x_size

#####################################################################
def clipRasterToShp(tif, shp, outputName, ndval = -9999):
    """ CLIPS RASTER FILE (jsut tifs?) TO EXTENT DEFINED BY A SHAPEFILE """
    
    print ('\nstarting: clip raster to shapefile')
    
     # Determine the new output feature class path and name
     #reproject input shapefile to match that of the tif
    """outfc = shp[0:-4]+'tempProj.shp'
    
    # Set output coordinate system
    ds=gdal.Open(tif)
    outCS=osr.SpatialReference()
    outCS.ImportFromWkt(ds.GetProjection())   
    ds = None
    
    # run project tool
    arcpy.Project_management(shp, outfc, outCS)"""
    
    # Fetch each feature from the cursor and examine the extent properties
    for row in arcpy.da.SearchCursor(shp, ["SHAPE@"]):
        extent = row[0].extent
        print("XMin: {0}, YMin: {1}".format(extent.XMin, extent.YMin))
        print("XMax: {0}, YMax: {1}".format(extent.XMax, extent.YMax))
        rectangle = str(extent.XMin)+ ' '+ str(extent.YMin)+ ' '+str(extent.XMax)+' '+ str(extent.YMax)
   
    arcpy.Clip_management(tif, rectangle, outputName, shp, ndval, 'ClippingGeometry')

def clipAndAlign(tif,shp,outputName,ndval='-9999'):
    # Replace a layer/table view name with a path to a dataset (which can be a layer file) or 
    #create the layer/table view within the script
    # The following inputs are layers or table views: "Topography_BM_Mosaic_ResetProp_3clip_fill10m.tif", 
    #"MT_NAIP_10m_BMROI.tif"
    arcpy.Clip_management(in_raster=tif,\
                          rectangle="254025 5194145 398555 5393615", \
                          out_raster='temp12345.tif', \
                          in_template_dataset=fileForProj, \
                          nodata_value=ndval, \
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

#####################################################################
def setRasterSpecs(inFile, clippingFile, filepath, toClip = False):
    """ SETS RASTER PROPERTIES: extent, resolution, spatial reference system, data type """
    
    print ('\nstarting" set raster specs')
    
    
    
    #file result of warp output
    outWarpName = inFile[0:-4]+'_ResetProp.tif'
    
    #open recently clipped raster
    myFile = gdal.Open(inFile)
    
    #resample myFile to 10 m resolution using bilinear interpolation
    #set new coordinate reference system
    #change data type
    #save file in current dir  as outFileName
    new_result = gdal.Warp(outWarpName, myFile, xRes=global_tgt_res, yRes=global_tgt_res, resampleAlg = gdal.GRIORA_Bilinear, \
                           dstSRS=global_tgt_srs, outputType=global_tgt_dt)#, dstSRS='EPSG:4326')
    new_result=None
    if toClip:    
        #file result of clip output
        outClipName = outWarpName[0:-4] + '_3clip.tif'
        
        #clipRasterToShp(outWarpName, clippingFile, outClipName)
        clipAndAlign(outWarpName, clippingFile, outClipName)
        
        


#####################################################################

if __name__ == '__main__':
    start = timer()
    
    if ContainsSubdirs:  #set this to true if you want to process files within subdirectories within the filepath 
        #ie files are within filepath directly
        for subDir in os.listdir(filePath):
            print (subDir)
            if os.path.isdir(os.path.join(filePath, subDir)): 
                currentDir = os.path.join(filePath,subDir)
                #if you can enter directory, look through it
                for myF in os.listdir(currentDir):
                    if myF.endswith('_clip1.tif'):
                        arcpy.Delete_management(os.path.join(currentDir,myF))
                for myF in os.listdir(currentDir):
                    if myF.endswith('.bil'): 
                        out_coor_system1="PROJCS['NAD_1983_UTM_Zone_12N',GEOGCS['GCS_North_American_1983',DATUM['D_North_American_1983',SPHEROID['GRS_1980',6378137.0,298.257222101]],PRIMEM['Greenwich',0.0],UNIT['Degree',0.0174532925199433]],PROJECTION['Transverse_Mercator'],PARAMETER['False_Easting',500000.0],PARAMETER['False_Northing',0.0],PARAMETER['Central_Meridian',-111.0],PARAMETER['Scale_Factor',0.9996],PARAMETER['Latitude_Of_Origin',0.0],UNIT['Meter',1.0]]"   
                        #in_coor_system1 ="GEOGCS['GCS_North_American_1983',DATUM['D_North_American_1983',SPHEROID['GRS_1980',6378137.0,298.257222101]],PRIMEM['Greenwich',0.0],UNIT['Degree',0.0174532925199433]]",\
                                                  
                        arcpy.RasterToOtherFormat_conversion(os.path.join(currentDir, myF), currentDir,'TIFF')
                        
                        myFile =  os.path.join(currentDir, myF.replace('.bil', '.tif'))
                        print ("\n*********************************************\nMy file is....\n",myFile)
                        myFile_prj = myFile.replace('.tif', '_prj.tif')
                        arcpy.ProjectRaster_management (in_raster=myFile, out_raster=myFile_prj,\
                                                        out_coor_system=out_coor_system1, resampling_type="BILINEAR")#,\
                                                        #in_coor_system = in_coor_system1)
                                                  
                                            
                        arcpy.Delete_management(myFile) #del intermediate file
                        print ("\n*********************************************\nMy file prj is....\n",myFile_prj)

                        #ext, crs, res = getRasterInfo(myFile)
                        #setRasterSpecs( myFile, clippingShp, currentDir, True)
                        
                        clipRasterToShp(myFile_prj, clippingShp,myFile_prj.replace('prj.tif','clip.tif'))
                        arcpy.Delete_management(myFile_prj) #del intermediate file
                    """elif myF.endswith('.tif'):
                        myFile =  myF
                        print ("\n*********************************************\nMy file is....\n",myFile)
                        print ("\nnew file created to [currentDir]... ",currentDir)
                        ext, crs, res = getRasterInfo(os.path.join(currentDir, myFile))
                        setRasterSpecs(os.path.join(currentDir, myFile), clippingShp, currentDir, True)"""
                        
    else:
        FilesList = []
        print ('files to processes are within the main directory (i.e. the set filepath)')
        for myFile in os.listdir(filePath):
            # and (myFile.endswith('Apr1SWE_30m_wgs_tps_predict_v2.tif')==False) and (myFile.endswith('DEF_30m_wgs_tps_predict_v2.tif')==False) and 
            if myFile.endswith('PRISM_ppt.tif'):
                FilesList.append(os.path.join(filePath, myFile))
        print ('\n\nFilesList:\n',FilesList)
        for myFile in FilesList:
            #if myFile.endswith('.tif') and (myFile.endswith('ResetProp.tif')==False):
            if myFile.endswith('ResetProp.tif'):
                print ("\n*********************************************\nMy file is....\n",myFile)
                print ("\nnew file created to [currentDir]... ",filePath)
                clipAndAlign(myFile,clippingShp, myFile.replace('.tif', '_3clip2.tif'))
            else:
                print ("\n*********************************************\nMy file is....\n",myFile)
                print ("\nnew file created to [currentDir]... ",filePath)
                ext, crs, res = getRasterInfo(myFile)
                setRasterSpecs(myFile, clippingShp, filePath, True)
                   
    elapsed = round(find_elapsed_time(start, timer()),3)
    print ("\n\nElapsed time = {}".format(elapsed))