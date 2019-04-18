# -*- coding: utf-8 -*-
"""
Created on Fri Feb 22 16:34:13 2019

@author: clairesimpson
"""

from sklearn.cluster import KMeans
from sklearn.externals import joblib
import matplotlib.pyplot as plt
import numpy as np
import gdal, ogr, osr
from os.path import join 
import os
from timeit import default_timer as timer
from sklearn.metrics import silhouette_samples, silhouette_score
import matplotlib.cm as cm
import arcpy

gdal.UseExceptions()

directory = r'F:/BMShareDrive'
start = timer()

def find_elapsed_time(start, end): # example time = round(find_elapsed_time(start, end),3) where start and end = timer()
    elapsed_min = (end-start)/60
    return float(elapsed_min)


def getProperties(VHRstack):
    img_ds = gdal.Open(VHRstack, gdal.GA_ReadOnly) # GDAL dataset

    gt = img_ds.GetGeoTransform()
    proj = img_ds.GetProjection()
    ncols = img_ds.RasterXSize
    nrows = img_ds.RasterYSize
    ndval = img_ds.GetRasterBand(1).GetNoDataValue() # should be -999 for all layers, unless using scene as input

    imgProperties = (gt, proj, ncols, nrows, ndval, img_ds.RasterCount)
    return imgProperties

def array_to_tif(inarr, outfile, imgProperties):

    # get properties from input
    (gt, proj, ncols, nrows, ndval, rastCnt) = imgProperties
    print (ndval)
    drvtif = gdal.GetDriverByName("GTiff")

    drv = drvtif.Create(outfile, ncols, nrows, 1, 3, options = [ 'COMPRESS=LZW' ]) # 1= number of bands (i think) and 3 = Data Type (16 bit signed)
    drv.SetGeoTransform(gt)
    drv.SetProjection(proj)
    drv.GetRasterBand(1).SetNoDataValue(ndval)
    drv.GetRasterBand(1).WriteArray(inarr)

    return outfile

def applyKmeansToSubset(inarr, numClusters, outModelName = "KMeans", returnData = False, sampleInterval = 10, ndval = -9999):
    print ("\nApplying Kmeans to Subset of data")
    #array(rows, cols)
    #array[pages,rows,cols,]
    testData = [inarr[i,:] for i in range(inarr.shape[0]) if (i%sampleInterval == 0 and np.all(inarr[i,:]!=ndval))] #sample every 3rd data point that is not ND
    testArray = np.array(testData).reshape(-1,nfeatures)
    print ('\nshape of test data array:',testArray.shape)
    
    kmeans = KMeans(n_clusters=numClusters, random_state=0).fit(testArray) #started at 11:06 am
    try:
        model_save = join(directory,"{}_{}Clus.pkl".format(outModelName, numClusters))
        joblib.dump(kmeans, model_save)
    except Exception as e:
        print ("Error: {}".format(e))
    
    if returnData:
        return(testArray, kmeans)
    
    return (kmeans)


def determineNumClusters(range_n_clusters, testArray):
    startNumCluster = timer()
    minclus,maxclus = range_n_clusters
    ssdifList = []
    for numClusters in range(minclus,maxclus):
        print ('\ndetermining data for cluster:',numClusters)
    # Create a subplot with 1 row and 2 columns
       
    
        # Initialize the clusterer with n_clusters value and a random generator
        # seed of 10 for reproducibility.
       
        kmeans = KMeans(n_clusters=numClusters, random_state=0).fit(testArray) 
        SSdif = kmeans.inertia_
        print (type(SSdif))
        try:
            model_save = join(directory,"{}_{}Clust.pkl".format("kmeans", numClusters))
            joblib.dump(kmeans, model_save)
        except Exception as e:
            print ("Error: {}".format(e))
        
        print("For n_clusters =", numClusters, "the ss dif is:", SSdif)#"The average silhouette_score is :", silhouette_avg)
        ssdifList.append(SSdif)
    elapsedNumCluster = round(find_elapsed_time(startNumCluster, timer()),3)
    print ("\n\nElapsed time to determine optimal clusters= {}".format(elapsedNumCluster))
    
    return (ssdifList) 



pcafiles = [r"F:/BMShareDrive/PrincipalComps/Topography/TOPO_Quant2_6PCA.tif",
             r"F:/BMShareDrive/PrincipalComps/Climate/CLIM_Cut_3PCA.tif",
             r"F:/BMShareDrive/PrincipalComps/Spectral/spectral2_3PCA1.tif"]

allfiles = [r"F:/BMShareDrive/Topography/ElevSlopeAspect_clip.tif",
            r"F:/BMShareDrive/Topography/MidSlopePosition.tif" ,
            r"F:/BMShareDrive/Topography/NED_SAGAWI2.tif",
            r"F:/BMShareDrive/Topography/NormalizedHeight.tif",
            r"F:/BMShareDrive/Topography/SlopeHeight.tif",                                                              
            r"F:/BMShareDrive/Topography/StandardizedHeight.tif",                                                         
            r"F:/BMShareDrive/Topography/TPI_01500.tif",                                                             
            r"F:/BMShareDrive/Topography/ValleyDepth.tif",                                                                
            r"F:/BMShareDrive/Climate/ZackClimateProcessed_keepPCA/Apr1SWE_30m_wgs_tps_predict_v2_ResetProp_3clip.tif",  
            r"F:/BMShareDrive/Climate/ZackClimateProcessed_keepPCA/DEF_30m_wgs_tps_predict_v2_ResetProp_3clip.tif",       
            r"F:/BMShareDrive/Climate/ZackClimateProcessed_keepPCA/PRISM_ppt_30yr_normal_800mM2_annual_Resampled.tif", 
            r"F:/BMShareDrive/Climate/ZackClimateProcessed_keepPCA/PRISM_tmax_30yr_normal_800mM2_annual_Resampled.tif", 
            r"F:/BMShareDrive/Climate/ZackClimateProcessed_keepPCA/SnowFreeDays_30m_wgs_tps_predict_ResetProp_3clip2.tif",
            r"F:/BMShareDrive/Climate/ZackClimateProcessed_keepPCA/srad_30m_wgs_tps_predict_ResetProp_3clip.tif",         
            r"F:/BMShareDrive/Climate/ZackClimateProcessed_keepPCA/tdew_1981-2010_annual_mean_R1_30m_ResetProp_3clip.tif",
            r"F:/BMShareDrive/Climate/ZackClimateProcessed_keepPCA/tmin_annual_30m_wgs_tps_predict_ResetProp_3clip.tif",  
            r"F:/BMShareDrive/Climate/ZackClimateProcessed_keepPCA/vpd_1981-2010_annual_mean_R1_30m_ResetProp_3clip.tif", 
            r"F:/BMShareDrive/Spectral/Landsat_SR_1984_2018_190_250_lcmsCONUS_mtbs_012219_ResetProp_clipclip.tif"]

imgProperties1 = getProperties(pcafiles[0])
imgProperties2 = getProperties(pcafiles[1])
imgProperties3 = getProperties(pcafiles[2])

rastCount = imgProperties1[5]+imgProperties2[5]+imgProperties3[5]
row= imgProperties1[3]
col = imgProperties1[2]
ndval = imgProperties1[4]

img = np.zeros((imgProperties1[3], imgProperties1[2], rastCount),np.float32 )
print (img.shape)

img_ds = gdal.Open(pcafiles[0], gdal.GA_ReadOnly) # GDAL dataset
for b in range(imgProperties1[5]):
    print ('\nb: {}'.format(b))
    img[:, :, b] = img_ds.GetRasterBand(b + 1).ReadAsArray()


img_ds = gdal.Open(pcafiles[1], gdal.GA_ReadOnly) # GDAL dataset
for b in range(imgProperties2[5]):
    print ('\nb: {}'.format(b+imgProperties1[5]))
    img[:, :, b+imgProperties1[5]] = img_ds.GetRasterBand(b + 1).ReadAsArray()


img_ds = gdal.Open(pcafiles[2], gdal.GA_ReadOnly) # GDAL dataset
for b in range(imgProperties3[5]):
    print ('\nb: {}'.format(b+imgProperties1[5]+imgProperties2[5]))
    img[:, :, b+imgProperties1[5]+imgProperties2[5]] = img_ds.GetRasterBand(b + 1).ReadAsArray()


numrows, numcols, nfeatures = img.shape #10338 (rows), 7303 (cols), 12 (layers)

img_d2 = img.reshape((numrows*numcols,nfeatures)) #reshape image into 2 dimensional space to prepare for kmeans
del img, img_ds #clear out space

mask = np.logical_or((np.logical_or(img_d2<(-3e30), img_d2<-50000000000000000000000000)),\
                                 np.logical_or(np.isnan(img_d2), img_d2==ndval)) #==None, =='nan'

img_d2[mask] =-9999


numClusters = 40

testData = [img_d2[i,:] for i in range(img_d2.shape[0]) if (i%12 == 0 and np.all(img_d2[i,:]!=-9999))] 
#sample every 3rd (%?) data point that is not ND

testArray = np.array(testData).reshape(-1,nfeatures)
print ('\nshape of test data array:',testArray.shape)



kmeans = KMeans(n_clusters=numClusters, random_state=0).fit(testArray) 
SSdif = kmeans.inertia_
print (type(SSdif))
try:
    model_save = join(directory,"{}_{}Clus.pkl".format("kmeans", numClusters))
    joblib.dump(kmeans, model_save)
except Exception as e:
    print ("Error: {}".format(e))

model_load = joblib.load(join(directory,"kmeansOnTestData.pkl")) # nd load
model_load25 = joblib.load(join(directory, "{}_{}Clus.pkl".format("kmeans", 25)))
plt.plot([25,30,40],[model_load25.inertia_, model_load.inertia_, SSdif])
         
OptimalClusters = determineNumClusters((10, 40), testArray)

sampleSSDist = kmeans.inertia_
centers = kmeans.cluster_centers_


#need to run
del testArray
img_d2_kmeans = kmeans.predict(img_d2)
print (img_d2_kmeans.shape)#img_d2_kmeans_class = img_d2_kmeans.labels_
img_d2_kmeans[mask[:,1]] = -9999 #mask out ndvals using one page of mask (has nfeatures pages)
img_d2_kmeans = img_d2_kmeans.reshape(numrows, numcols) #pages, rows, cols
array_to_tif(img_d2_kmeans,r"F:/BMShareDrive/WildPCs_KmeansClus30_nd.tif", imgProperties1)

elapsed = round(find_elapsed_time(start, timer()),3)
print ("\n\nElapsed time = {}".format(elapsed))

#################################
fp=r'\\166.2.126.25\teui1\4_Claire\BobMarshall\Data\Raster\LayerGroupsForcLHA\wildNonPC\integer'
arcpy.env.workspace = fp
intFiles = (i for i in os.listdir(fp) if i.endswith('.tif'))

#to create following string:
fold = ''
for i in intFiles:
    fold+=i+';'
intFiles = fold[:-1]    
intFiles = "Apr1SWE_30m_wgs_tps_predict_v2_ResetProp_3clip_wildInt.tif;DEF_30m_wgs_tps_predict_v2_ResetProp_3clip_wildInt.tif;ElevSlopeAspect_clip_wildInt_b1.tif;ElevSlopeAspect_clip_wildInt_b2.tif;ElevSlopeAspect_clip_wildInt_b3.tif;Landsat_SR_1984_2018_190_250_lcmsCONUS_mtbs_012219_ResetProp_clipclip_wildInt_b1.tif;Landsat_SR_1984_2018_190_250_lcmsCONUS_mtbs_012219_ResetProp_clipclip_wildInt_b10.tif;Landsat_SR_1984_2018_190_250_lcmsCONUS_mtbs_012219_ResetProp_clipclip_wildInt_b11.tif;Landsat_SR_1984_2018_190_250_lcmsCONUS_mtbs_012219_ResetProp_clipclip_wildInt_b12.tif;Landsat_SR_1984_2018_190_250_lcmsCONUS_mtbs_012219_ResetProp_clipclip_wildInt_b13.tif;Landsat_SR_1984_2018_190_250_lcmsCONUS_mtbs_012219_ResetProp_clipclip_wildInt_b14.tif;Landsat_SR_1984_2018_190_250_lcmsCONUS_mtbs_012219_ResetProp_clipclip_wildInt_b15.tif;Landsat_SR_1984_2018_190_250_lcmsCONUS_mtbs_012219_ResetProp_clipclip_wildInt_b16.tif;Landsat_SR_1984_2018_190_250_lcmsCONUS_mtbs_012219_ResetProp_clipclip_wildInt_b17.tif;Landsat_SR_1984_2018_190_250_lcmsCONUS_mtbs_012219_ResetProp_clipclip_wildInt_b18.tif;Landsat_SR_1984_2018_190_250_lcmsCONUS_mtbs_012219_ResetProp_clipclip_wildInt_b19.tif;Landsat_SR_1984_2018_190_250_lcmsCONUS_mtbs_012219_ResetProp_clipclip_wildInt_b2.tif;Landsat_SR_1984_2018_190_250_lcmsCONUS_mtbs_012219_ResetProp_clipclip_wildInt_b3.tif;Landsat_SR_1984_2018_190_250_lcmsCONUS_mtbs_012219_ResetProp_clipclip_wildInt_b4.tif;Landsat_SR_1984_2018_190_250_lcmsCONUS_mtbs_012219_ResetProp_clipclip_wildInt_b5.tif;Landsat_SR_1984_2018_190_250_lcmsCONUS_mtbs_012219_ResetProp_clipclip_wildInt_b6.tif;Landsat_SR_1984_2018_190_250_lcmsCONUS_mtbs_012219_ResetProp_clipclip_wildInt_b7.tif;Landsat_SR_1984_2018_190_250_lcmsCONUS_mtbs_012219_ResetProp_clipclip_wildInt_b8.tif;Landsat_SR_1984_2018_190_250_lcmsCONUS_mtbs_012219_ResetProp_clipclip_wildInt_b9.tif;MidSlopePosition_wildInt.tif;NED_SAGAWI2_wildInt.tif;NormalizedHeight_wildInt.tif;PRISM_ppt_30yr_normal_800mM2_annual_Resampled_wildInt.tif;PRISM_tmax_30yr_normal_800mM2_annual_Resampled_wildInt.tif;SlopeHeight_wildInt.tif;SnowFreeDays_30m_wgs_tps_predict_ResetProp_3clip2_wildInt.tif;srad_30m_wgs_tps_predict_ResetProp_3clip_wildInt.tif;StandardizedHeight_wildInt.tif;tdew_1981-2010_annual_mean_R1_30m_ResetProp_3clip_wildInt.tif;tmin_annual_30m_wgs_tps_predict_ResetProp_3clip_wildInt.tif;TPI_01500_wildInt.tif;ValleyDepth_wildInt.tif;vpd_1981-2010_annual_mean_R1_30m_ResetProp_3clip_wildInt.tif"

arcpy.CompositeBands_management(in_rasters=intFiles, out_raster='intStack.tif')
allfilesPCA = join(fp,'intStack.tif') #nb this is not pca data..
#allfilesPCA = r'F:\BMShareDrive\AllFilesPCA_Arc.tif'
imgProperties1 = getProperties(allfilesPCA)

rastCount = imgProperties1[5]
row= imgProperties1[3]
col = imgProperties1[2]
ndval = imgProperties1[4]

img = np.zeros((imgProperties1[3], imgProperties1[2], rastCount),np.float32 )
print (img.shape)

img_ds = gdal.Open(allfilesPCA, gdal.GA_ReadOnly) # GDAL dataset
for b in range(rastCount):
    print ('\nb: {}'.format(b))
    img[:, :, b] = img_ds.GetRasterBand(b + 1).ReadAsArray()

##
    
numrows, numcols, nfeatures = img.shape #10338 (rows), 7303 (cols), 12 (layers)

img_d2 = img.reshape((numrows*numcols,nfeatures)) #reshape image into 2 dimensional space to prepare for kmeans
del img, img_ds #clear out space

mask = np.logical_or((np.logical_or(img_d2<(-3e30), img_d2<-50000000000000000000000000)),\
                                 np.logical_or(np.isnan(img_d2), img_d2==ndval)) #==None, =='nan'

img_d2[mask] =-9999


numClusters = 30

testData = [img_d2[i,:] for i in range(img_d2.shape[0]) if (i%12 == 0 and np.all(img_d2[i,:]!=-9999))] 
#sample every 3rd (%?) data point that is not ND

testArray = np.array(testData).reshape(-1,nfeatures)
print ('\nshape of test data array:',testArray.shape)



kmeans = KMeans(n_clusters=numClusters, random_state=0).fit(testArray) 
SSdif = kmeans.inertia_
print (type(SSdif))
try:
    model_save = join(directory,"{}_{}Clus.pkl".format("kmeans", numClusters))
    joblib.dump(kmeans, model_save)
except Exception as e:
    print ("Error: {}".format(e))

img_d2_kmeans = kmeans.predict(img_d2)
print (img_d2_kmeans.shape)#img_d2_kmeans_class = img_d2_kmeans.labels_
img_d2_kmeans[mask[:,1]] = -9999 #mask out ndvals using one page of mask (has nfeatures pages)
img_d2_kmeans = img_d2_kmeans.reshape(numrows, numcols) #pages, rows, cols
array_to_tif(img_d2_kmeans,r"F:/BMShareDrive/FullWild_kmeans30Clus.tif", imgProperties1)

elapsed = round(find_elapsed_time(start, timer()),3)
print ("\n\nElapsed time = {}".format(elapsed))
