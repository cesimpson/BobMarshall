# -*- coding: utf-8 -*-
"""
Created on Tue Apr 16 09:24:33 2019

@author: clairesimpson
"""

import arcpy
import os 
import numpy as np
import matplotlib.pyplot as plt
import gdal

fp=r'F:\BMShareDrive\30m_origLayers\clhs_outputs\cLHS_run_9'

shp = os.path.join(fp, 'clhsPts_10m_1500_10000_9.shp')
#arr = arcpy.da.FeatureClassToNumPyArray(shp, ('FID', 'Cost', 'DEF', 'Elev'))
attList = ['Cost', 'DEF', 'Elev', 'Slope', 'LS13_NDCI', 'LS14bright', 'LS7_NDVI', 'SolarRad', 'StdHeight',
           'tmin', 'TPI', 'Wetness', 'PI', 'gensym', 'geomorphon', 'elevstr']

ar= np.zeros((1500, len(attList)))
i=-1
with arcpy.da.SearchCursor(shp, attList) as cursor:
    for row in cursor:
        i+=1
        ar[i]=row
  
newDir = os.path.join(fp, 'Histograms')      
#os.mkdir(newDir)      

fp = r'\\166.2.126.25\teui1\4_Claire\BobMarshall\Data\Raster\LayerGroupsForcLHA\10mInt\NotClippedToTrailBuf'
arcpy.env.workspace = newDir
tifList = [] 
tifList =[r"//166.2.126.25/teui1/4_Claire/BobMarshall/Data/Vector/R1_Trails_subset/TrailsCost_5c3_10m4_reclas_waterMask.tif ",
          r'//166.2.126.25/teui1/4_Claire/BobMarshall/Data/Raster/LayerGroupsForcLHA/10mInt/NotClippedToTrailBuf/DEF_30m_wgs_tps_predict_v2_ResetProp_3clipInt.tif ',r'//166.2.126.25/teui1/4_Claire/BobMarshall/Data/Raster/LayerGroupsForcLHA/10mInt/NotClippedToTrailBuf/ElevSlopeAspect_clipInt_b1.tif ',
          r'//166.2.126.25/teui1/4_Claire/BobMarshall/Data/Raster/LayerGroupsForcLHA/10mInt/NotClippedToTrailBuf/ElevSlopeAspect_clipInt_b2.tif ',
          r'//166.2.126.25/teui1/4_Claire/BobMarshall/Data/Raster/LayerGroupsForcLHA/10mInt/NotClippedToTrailBuf/Landsat_SR_1984_2018_190_250_lcmsCONUS_mtbs_012219_ResetProp_clipclipInt_b13.tif ',
          r'//166.2.126.25/teui1/4_Claire/BobMarshall/Data/Raster/LayerGroupsForcLHA/10mInt/NotClippedToTrailBuf/Landsat_SR_1984_2018_190_250_lcmsCONUS_mtbs_012219_ResetProp_clipclipInt_b14.tif ',
          r'//166.2.126.25/teui1/4_Claire/BobMarshall/Data/Raster/LayerGroupsForcLHA/10mInt/NotClippedToTrailBuf/Landsat_SR_1984_2018_190_250_lcmsCONUS_mtbs_012219_ResetProp_clipclipInt_b7.tif ',
          r'//166.2.126.25/teui1/4_Claire/BobMarshall/Data/Raster/LayerGroupsForcLHA/10mInt/NotClippedToTrailBuf/srad_30m_wgs_tps_predict_ResetProp_3clipInt.tif ',
          r'//166.2.126.25/teui1/4_Claire/BobMarshall/Data/Raster/LayerGroupsForcLHA/10mInt/NotClippedToTrailBuf/StandardizedHeightInt.tif ',
          r'//166.2.126.25/teui1/4_Claire/BobMarshall/Data/Raster/LayerGroupsForcLHA/10mInt/NotClippedToTrailBuf/tmin_annual_30m_wgs_tps_predict_ResetProp_3clipInt.tif ',
          r'//166.2.126.25/teui1/4_Claire/BobMarshall/Data/Raster/LayerGroupsForcLHA/10mInt/NotClippedToTrailBuf/TPI_01500Int.tif ',
          r'//166.2.126.25/teui1/4_Claire/BobMarshall/Data/Raster/LayerGroupsForcLHA/10mInt/NotClippedToTrailBuf/NED_SAGAWI2Int.tif ',
          r'//166.2.126.25/teui1/4_Claire/BobMarshall/Data/Raster/LayerGroupsForcLHA/10mInt/NotClippedToTrailBuf/PI_50IntClip.tif ',
          r'//166.2.126.25/teui1/4_Claire/BobMarshall/Data/Raster/LayerGroupsForcLHA/10mInt/NotClippedToTrailBuf/gensym-sup-class-latest_prj_10m.tif',
          r'//166.2.126.25/teui1/4_Claire/BobMarshall/Data/Raster/LayerGroupsForcLHA/10mInt/NotClippedToTrailBuf/Geomorphons.tif',
          r'//166.2.126.25/teui1/4_Claire/BobMarshall/Data/Raster/LayerGroupsForcLHA/10mInt/NotClippedToTrailBuf/StreamElevDist_5_focalMean_con3Int2.tif']

print (len(tifList)==len(attList))
numBins=30  
for var in range(len(attList)):
    print (attList[var], '\n',tifList[var])
    tif = tifList[var]
    img_ds = gdal.Open(tif, gdal.GA_ReadOnly)
    tif_ar = img_ds.GetRasterBand(1).ReadAsArray()
    ndval = img_ds.GetRasterBand(1).GetNoDataValue()
    print ('no data val:', ndval)
    
    del(img_ds)
    def_list = tif_ar.flatten().tolist()
    del(tif_ar)
    def_list2 =[i for i in def_list if i!=ndval]
    if attList[var] =='Cost':
        def_list2 =[i for i in def_list if i!=128 and i!=-128]
    print ('max:,',max(def_list2))
    print ('min:', min(def_list2))
    
    fig = plt.figure()
#    plt.xlabel('Value')
#    plt.ylabel('Count')
    plt.title('Histogram of: '+attList[var])
    plt.xlabel('Value')
    ax1 = fig.add_subplot(111)
    ax1.hist(def_list2, numBins, facecolor='blue')
    ax1.set_ylabel('Count for Full Raster', color = 'blue')
    ax2 = ax1.twinx()
    ax2.hist(ar[:,var], numBins, facecolor='red', alpha=0.5)
    ax2.set_ylabel('Count for cLHS points', color = 'red')
    
   
    #plt.subplots_adjust(top=1.17)
   
    plt.savefig(os.path.join(newDir,'Histogram2_{}bins_{}.png'.format(numBins, attList[var])))
    plt.close()
#    
#    
#
#ras_fp = r'\\166.2.126.25\teui1\4_Claire\BobMarshall\Data\Raster\LayerGroupsForcLHA\10mInt\NotClippedToTrailBuf'
#def_tif = os.path.join(ras_fp, 'DEF_30m_wgs_tps_predict_v2_ResetProp_3clipInt.tif')
#img_ds = gdal.Open(def_tif, gdal.GA_ReadOnly)
#def_ar = img_ds.GetRasterBand(1).ReadAsArray()#.astype(int)
#def_list = def_ar.flatten()
#def_list2 =[i for i in def_list if i>0]
#plt.xlabel('Value')
#plt.ylabel('Count')
#print ('def')
#plt.title('Histogram of: '+'def')
#n,bins,patches = plt.hist(def_list2, numBins, facecolor='blue', alpha=0.5)
##plt.subplots_adjust(top=1.17)
#   
#plt.savefig(os.path.join(newDir,'Histogram_{}bins_{}.png'.format(numBins, 'defRas')))
#plt.close()

   