# -*- coding: utf-8 -*-
"""
Created on Thu Feb 28 14:34:26 2019

@author: clairesimpson
"""

#convert rasters in a folder to integer data type


import arcpy
from arcpy.sa import *
import os
#arcpy.env.extent = arcpy.Extent(230130, 3875790, 1208430, 5065830)

arcpy.env.overwriteOutput=True
# Check out the ArcGIS Spatial Analyst extension license
arcpy.CheckOutExtension("Spatial")

fpList = [r'\\166.2.126.25\teui1\4_Claire\BobMarshall\Data\Raster\LayerGroupsForcLHA\10mInt\NotClippedToTrailBuf']

fileEnd = '.tif'
resample30 = False
composite = False    

if fileEnd == '.tif':
    BandRef = '/Band_'
elif fileEnd =='.img':
    BandRef = '/Layer_'
    

for filepath in fpList:
    out_filepath = r'\\166.2.126.25\teui1\4_Claire\BobMarshall\Data\Raster\LayerGroupsForcLHA\10mInt\NotClippedToTrailBuf' #r'\\166.2.126.25\teui1\4_Claire\R4 Erosion\KFactor\RFA_inputs'
    
    for f in os.listdir(filepath):
        if f.endswith(fileEnd) and (('TRI_' in f) or ('PI_5' in f)):#and ('LSSpectral' not in f) and ('PRISM' not in f) and ('Elev' not in f) and ('predict' not in f) and ('Geomorph' not in f):#and ('DEF' not in f):
            print (f, 'is current f')
            raster = Raster(os.path.join(filepath,f))
            d=arcpy.Describe(raster)
            bandCount = d.bandCount
            print (bandCount)
            
            if bandCount ==1:
                print ('\nExtrema of',f,raster.minimum, raster.maximum)
                if raster.maximum<100:
                    ## NB if this fails, may need to explicitly calculate stats
                    #arcpy.CalculateStatistics_management(in_raster_dataset="F:/BMShareDrive/Topography/SlopeHeight.tif", 
                     #                                    x_skip_factor="1", y_skip_factor="1", ignore_values="", 
                      #                                   skip_existing="OVERWRITE", area_of_interest="Feature Set")
                    outRas = Int(1000*(raster) + 0.5)
                    out_filename = f.replace(fileEnd,'Int'+fileEnd)
                    outRas.save(os.path.join(out_filepath, out_filename))
                else:
                    outRas = Int(10*(raster) + 0.5)
                    out_filename = f.replace(fileEnd,'Int'+fileEnd)
                    outRas.save(os.path.join(out_filepath, out_filename))
                
            else:
                print (f,' is multiband raster with bands #',bandCount)
                if ('LS' in f):
                    bandL = [2,3,4,5]#[6,7,9,10,11,12,13]
                else:
                    bandL=range(bandCount)
                for idx in bandL:
                    print (idx)
                    f_band = f.replace(fileEnd, fileEnd+BandRef+str(idx+1)) #Band (tif) or Layer (img)
                    raster = Raster(os.path.join(filepath,f_band))
                    print ('\nExtrema of',f,raster.minimum, raster.maximum, '\n')
                    if raster.maximum<100:
                        outRas = Int(1000*(raster) + 0.5)
                        out_filename = f.replace(fileEnd,'Int_b'+str(idx+1)+fileEnd)
                        outRas.save(os.path.join(out_filepath, out_filename))
                    else:
                        outRas = Int(10*(raster) + 0.5)
                        out_filename = f.replace(fileEnd,'Int_b'+str(idx+1)+fileEnd)
                        outRas.save(os.path.join(out_filepath, out_filename))
                        
   
if resample30 == True:                          
    out_filepath = r'F:\BMShareDrive\Int'   
    for f in os.listdir(out_filepath):
        if f.endswith(fileEnd):
            myfile = os.path.join(out_filepath, f)
            outfilename = myfile.replace(fileEnd,'30m'+fileEnd)
            arcpy.Resample_management(myfile,outfilename,30,'BILINEAR')
            
if composite:
    fp=r'\\166.2.126.25\teui1\4_Claire\R4 Erosion\KFactor\RFA_inputs'
    rlist = [os.path.join(fp,f) for f in os.listdir(fp) if (f.endswith('Int.tif') or f.endswith('Int.img') or (f.endswith('.tif') and'Int_b' in f))]
    print (rlist, '\nLength:',len(rlist))
    outname = r'\\166.2.126.25\teui1\4_Claire\R4 Erosion\KFactor\RFA_inputs\RFAinput_composite1.tif'
    arcpy.CompositeBands_management(rlist, outname)
    
    
    
try:  
    del (raster, f, d, bandCount)
except:
    print ('not del')
    
    
    
    
    