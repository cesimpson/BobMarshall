# -*- coding: utf-8 -*-
"""
Created on Thu Feb 14 13:42:50 2019

@author: clairesimpson
"""
import os
import arcpy
from timeit import default_timer as timer

def find_elapsed_time(start, end): # example time = round(find_elapsed_time(start, end),3) where start and end = timer()
    elapsed_min = (end-start)/60
    return float(elapsed_min)
start = timer()
filePath = r'F:\BMShareDrive'
keep_shp = r'\\166.2.126.25\teui1\4_Claire\BobMarshall\Data\Vector\R1_Trails_subset\ExclusionLayer_BM_Keep.shp'
clip_shp = r'\\166.2.126.25\teui1\4_Claire\BobMarshall\Data\Vector\MT633\BM_wilderness.shp'

origFiles = []
def clipGroup(currentFileEnding, newFileEnding, clipTemplate, bbox):
    for folder in os.listdir(filePath):
        print ('\nFolder', folder)
        try:
            for subdir in os.listdir(folder):
                print ('\nsubdir',subdir)
                try:
                    for file in os.listdir(os.path.join(filePath,folder,subdir)):
                        # clip file
                        
                        if file.endswith(currentFileEnding):
                            print (file)
                            origFiles.append(os.path.join(filePath,folder,subdir,file))
                except:
                    file=subdir #subdirectory is actually a file
                    if file.endswith(currentFileEnding):
                        print (file)
                        origFiles.append(os.path.join(filePath,folder,file))
        except:
            print (folder, 'IS NOT A FOLDER')
            
    #origFiles = [r'F:\BMShareDrive\Climate\ZackClimateProcessed\srad_30m_wgs_tps_predict_ResetProp_3clip.tif']           
                #
    for file in origFiles:
        
        # Replace a layer/table view name with a path to a dataset (which can be a layer file) or create the layer/table view within the script
    # The following inputs are layers or table views: "MT_NAIP_10m_BMROI.tif", "BM_wilderness"
        arcpy.Clip_management(in_raster=file, rectangle=bbox, \
                          out_raster=file.replace(currentFileEnding, newFileEnding),\
                          in_template_dataset=clipTemplate, \
                          nodata_value="-9999", clipping_geometry="ClippingGeometry", maintain_clipping_extent="NO_MAINTAIN_EXTENT")

clipGroup(currentFileEnding = '.tif', newFileEnding = '_wild.tif', \
          clipTemplate = keep_shp, bbox = "300312.736779295 5233027.02884447 373335.793726064 5336400.05700031") 

#keep_rectangle="301265 5233025 373195 5336405"

#clipGroup('_wild.tif', 'wildKeep.tif', keep_shp,keep_rectangle)   


# Replace a layer/table view name with a path to a dataset (which can be a layer file) or create the layer/table view within the script
# The following inputs are layers or table views: "MT_NAIP_10m_BMROI.tif", "ExclusionLayer_BM_Keep"

elapsed = round(find_elapsed_time(start, timer()),3)

print ("\n\nElapsed time = {}".format(elapsed))
