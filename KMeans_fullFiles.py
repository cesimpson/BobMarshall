# -*- coding: utf-8 -*-
"""
Created on Fri Mar 29 16:17:10 2019

@author: clairesimpson
"""

# -*- coding: utf-8 -*-
"""
Created on Fri Feb 22 16:34:13 2019

@author: clairesimpson
"""

#########################################################################################
#houskeeping: imports, settings
#########################################################################################
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

directory = r'F:/BMShareDrive' #where everything gets saved to
start = timer()

rangeForClusters = ''#(15,30) #set this in format (10, 40) if want to determine optimal number of clusters
numClusters = 30 #set this is you dont want to go through trouble of determining optimal number of clusters
# or set when you've already determined optimal number of clusters 

out_cluster_map = 'kmeans_map_{}.tif'.format(numClusters)
#########################################################################################
#define functions
#########################################################################################
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

def UNUSED_applyKmeansToSubset(inarr, numClusters, outModelName = "KMeans", returnData = False, sampleInterval = 10, ndval = -9999):
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
    #will calculate kmeans model for each number of clusters in range. Can then plot sum of squares difference to see where
    # lowest points with lowest number of clusters occurs( i.e. where the best tradeoff is bw # clus and ss-dif)
    if range_n_clusters=='':
        print ("range of clusters to try not set.. returning 0")
        return (0)
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



#########################################################################################
# name/call files to use in kmean clustering
#########################################################################################
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

allfiles = [os.path.join(r'F:\BMShareDrive\30m_origLayers', 
                         f) for f in os.listdir(r'F:\BMShareDrive\30m_origLayers') if f.endswith('.tif') or f.endswith('.img')]
for x in allfiles:
    print (x)
#########################################################################################
# get image properties to 
#(1) use to create 3d array to read all files into and 
#(2) save for export of kmeans maps 
#########################################################################################
print ('Getting image properties for stack and save..')
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


#########################################################################################
#create and apply mask to remove no data values
#########################################################################################
print ("building no data mask..")
mask = np.logical_or((np.logical_or(img_d2<(-3e30), img_d2<-50000000000000000000000000)),\
                                 np.logical_or(np.isnan(img_d2), img_d2==ndval)) #==None, =='nan'

img_d2[mask] =-9999


#########################################################################################
# generate test data from full dataset (so only training kmeans on subset of data to decrease
#processing time) 
#NB number after % is how often to sample (larger # = smaller test sample size)
#########################################################################################
print ("Subsetting out test data to build kmeans model")
testData = [img_d2[i,:] for i in range(img_d2.shape[0]) if (i%12 == 0 and np.all(img_d2[i,:]!=-9999))] 
#sample every 3rd (%?) data point that is not ND

testArray = np.array(testData).reshape(-1,nfeatures)
print ('\nshape of test data array:',testArray.shape)


#########################################################################################
# determine number of optimal clusters using elbow method
#will need to manually look at plot to determine where 'elbow' is 
#########################################################################################
print ("Determining number of clusters to use...")
#will calculate kmeans model for each number of clusters in range. Can then plot sum of squares difference to see where
# lowest points with lowest number of clusters occurs( i.e. where the best tradeoff is bw # clus and ss-dif)
OptimalClusters_ssdifList = determineNumClusters(range_n_clusters=rangeForClusters, testArray=testArray)
try:    
    plt.plot(range(rangeForClusters[0], rangeForClusters[1]), OptimalClusters_ssdifList)
    plt.show()
except:
    print ('Did not determine optimal number of clusters.')


#########################################################################################
#perform kmeans classification on subsampled data with x number of clusters (& save model)
#########################################################################################
print ("Generating kmeans clusters on test data [ie training model]")
kmeans = KMeans(n_clusters=numClusters, random_state=0).fit(testArray) 
SSdif = kmeans.inertia_
#centers = kmeans.cluster_centers_

print (type(SSdif))
try:
    print ("Saving model pkl...")
    model_save = join(directory,"{}_{}Clus.pkl".format("kmeans", numClusters))
    joblib.dump(kmeans, model_save)
except Exception as e:
    print ("Error: {}".format(e))


#########################################################################################
# if want to reload previous model... [and see what elbow plot of prev models w dif number of clusters looks like]
#########################################################################################
model_load = joblib.load(join(directory,"kmeansOnTestData.pkl")) # nd load
model_load25 = joblib.load(join(directory, "{}_{}Clus.pkl".format("kmeans", 25)))
plt.plot([25,30,40],[model_load25.inertia_, model_load.inertia_, SSdif])
plt.show()

#########################################################################################
# applying kmeans model to entire image stack 
# masking no data values from kmeans cluster map
# exporting cluster map to tif
#########################################################################################
del testArray
img_d2_kmeans = kmeans.predict(img_d2)
print (img_d2_kmeans.shape, 'is shape of clustered stack')#img_d2_kmeans_class = img_d2_kmeans.labels_
img_d2_kmeans[mask[:,1]] = -9999 #mask out ndvals using one page of mask (has nfeatures pages)
img_d2_kmeans = img_d2_kmeans.reshape(numrows, numcols) #pages, rows, cols
array_to_tif(img_d2_kmeans,os.path.join(directory,out_cluster_map), imgProperties1)



elapsed = round(find_elapsed_time(start, timer()),3)
print ("\n\nElapsed time = {}".format(elapsed))
