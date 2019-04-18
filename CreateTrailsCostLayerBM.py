# -*- coding: utf-8 -*-
"""
Created on Wed Mar  6 09:37:16 2019

@author: clairesimpson


#select trails in full R1 trails gdb that intersect quarter mi trail buffers
# buffer this maintianed AND nonmaintained trails subsection to quarte mi (1000), and half mi (100)

#add 4 buffer layers together by arcpy add
    
# reclassify layers 
    #>=1000: 1
    #>=100:2
    #>=10: 3
    #>= 1:4
    
"I selected all trails in R1 that intersected the maintained trails and assigned the maintained trails values of 1 and 2 for pixels within the half and 
quarter mi trail buffer, respectively. Then for the trails in R1 that were not part of the maintained trails but theoretically connect to a mainstem trail, 
 I assigned values of 3 or 4, depending on distance from trail. "
 
 "I weighted both ¼ and ½ mi buffers of non-maintained trails that are within 1 mile of mainstem trail more favorably than the rest of 
 the ¼ and ½ mi buffers of non-maintained trails"

"""
import arcpy
import os
from arcpy.sa import *
fp=r'//166.2.126.25/teui1/4_Claire/BobMarshall/Data/Vector'

arcpy.env.workspace = os.path.join(fp, 'R1_Trails_subset')
arcpy.env.overwriteOutput=True

coordSys = "PROJCS['NAD_1983_UTM_Zone_12N',GEOGCS['GCS_North_American_1983',DATUM['D_North_American_1983',SPHEROID['GRS_1980',6378137.0,298.257222101]],PRIMEM['Greenwich',0.0],UNIT['Degree',0.0174532925199433]],PROJECTION['Transverse_Mercator'],PARAMETER['False_Easting',500000.0],PARAMETER['False_Northing',0.0],PARAMETER['Central_Meridian',-111.0],PARAMETER['Scale_Factor',0.9996],PARAMETER['Latitude_Of_Origin',0.0],UNIT['Meter',1.0]]"


FullTrails =os.path.join (r'\\166.2.126.25\teui1\4_Claire\BobMarshall\Data\Vector\R1_Trails_subset','R1_Trails_subset.shp')
outProj = FullTrails.replace('.shp','proj.shp')
print (outProj)
arcpy.Project_management (in_dataset=FullTrails, out_dataset=outProj,
                          out_coor_system=coordSys)#, transform_method='WGS_1984_to_NAD_1983')#, {in_coor_system}, {preserve_shape}, {max_deviation}, {vertical})

#select features from target (in) layer based on relationship (overlap type) with source (select) layer
#select features:The features in the input feature layer will be selected based on their relationship 
    #to the features from this layer or feature class.


############################################################
# Create buffers around trails
arcpy.Buffer_analysis(in_features=r'\\166.2.126.25\teui1\4_Claire\BobMarshall\Data\Vector\BMWCTrails.gdb\BMWCTrails.gdb\Trails_Final',
                      out_feature_class=os.path.join(fp, 'R1_Trails_subset',"Trails_QuartMi.shp"),
                      buffer_distance_or_field="0.25 Miles", 
                      line_side="FULL", line_end_type="ROUND",
                      dissolve_option="ALL", dissolve_field="", 
                      method="PLANAR")

arcpy.Buffer_analysis(in_features=r'\\166.2.126.25\teui1\4_Claire\BobMarshall\Data\Vector\BMWCTrails.gdb\BMWCTrails.gdb\Trails_Final', 
                      out_feature_class=os.path.join(fp, 'R1_Trails_subset',"Trails_HalfMi.shp"),
                      buffer_distance_or_field="0.5 Miles", line_side="FULL", 
                      line_end_type="ROUND", dissolve_option="ALL", dissolve_field="", 
                      method="PLANAR")

arcpy.Buffer_analysis(in_features=r'\\166.2.126.25\teui1\4_Claire\BobMarshall\Data\Vector\BMWCTrails.gdb\BMWCTrails.gdb\Trails_Final', 
                      out_feature_class=os.path.join(fp, 'R1_Trails_subset',"Trails_OneMi.shp"),
                      buffer_distance_or_field="1.0 Miles", line_side="FULL", 
                      line_end_type="ROUND", dissolve_option="ALL", dissolve_field="", 
                      method="PLANAR")

MaintBuffer_half =os.path.join(fp, 'R1_Trails_subset',"Trails_HalfMi.shp")
MaintBuffer_quart =os.path.join(fp, 'R1_Trails_subset',"Trails_QuartMi.shp")
MaintBuffer_one =os.path.join(fp, 'R1_Trails_subset',"Trails_OneMi.shp")

selectTrails=arcpy.SelectLayerByLocation_management(in_layer=outProj,overlap_type='INTERSECT',select_features=MaintBuffer_quart)

arcpy.Buffer_analysis(in_features=selectTrails,out_feature_class=os.path.join(fp, 'R1_Trails_subset','halfMi.shp'), 
                      buffer_distance_or_field="0.5 Miles", line_side="FULL",line_end_type="ROUND", 
                      dissolve_option="ALL", 
                      dissolve_field="", 
                      method="PLANAR")

arcpy.Buffer_analysis(in_features=selectTrails,
                      out_feature_class=os.path.join(fp, 'R1_Trails_subset','quarterMi.shp'), 
                      buffer_distance_or_field="0.25 Miles", 
                      line_side="FULL", 
                      line_end_type="ROUND", 
                      dissolve_option="ALL", 
                      dissolve_field="", 
                      method="PLANAR")

#############################################################
#create path to shp objects
FullBuffer_halfmi = os.path.join(fp, 'R1_Trails_subset','halfMi.shp')
FullBuffer_quartmi = os.path.join(fp, 'R1_Trails_subset','quarterMi.shp')
#############################################################

# add Buf ID field and populate
#########################
for item, val in {FullBuffer_halfmi:1,MaintBuffer_half:1000,FullBuffer_quartmi:10,MaintBuffer_quart:10000,MaintBuffer_one:100}.items():
    print (item, val)
    try:
        arcpy.AddField_management(item,'BufID','SHORT')
        with arcpy.da.UpdateCursor(item, ['BufID']) as cursor:
            for row in cursor:
                row[0]= val
                cursor.updateRow(row)
    except:
        with arcpy.da.UpdateCursor(item, ['BufID']) as cursor:
            for row in cursor:
                row[0]= val
                cursor.updateRow(row)
        
        print('field already exists')
    del row
   

############################################################
# =============================================================================
# arcpy.Merge_management(inputs = [FullBuffer_halfmi,MaintShp_half,FullBuffer_quartmi,MaintShp_quart],
#                        output='merged2.shp', field_mappings='Sum')
# 
# #check if merge file is correct:
# with arcpy.da.SearchCursor('merged2.shp',['BufID']) as cursor:
#     for row in cursor:
#         print(row[0], 'is val of buf id for row...')
# del row       
# arcpy.PolygonToRaster_conversion(in_features ='merged.shp', value_field='BufID', out_rasterdataset='mergedTif.tif', cellsize=5)
# 
# =============================================================================

############################################################

        
arcpy.PolygonToRaster_conversion(in_features = FullBuffer_halfmi, value_field='BufID', out_rasterdataset='halfMi_raster.tif',cellsize = 5)
arcpy.PolygonToRaster_conversion(in_features = FullBuffer_quartmi, value_field='BufID',out_rasterdataset='quarterMi_raster.tif',cellsize = 5)

arcpy.PolygonToRaster_conversion(in_features = MaintBuffer_half, value_field='BufID', out_rasterdataset='halfMi_Maintraster.tif',cellsize = 5)
arcpy.PolygonToRaster_conversion(in_features = MaintBuffer_quart, value_field='BufID', out_rasterdataset='quartMi_Maintraster.tif',cellsize = 5)
arcpy.PolygonToRaster_conversion(in_features = MaintBuffer_one, value_field='BufID', out_rasterdataset='oneMi_Maintraster.tif',cellsize = 5)


arcpy.MosaicToNewRaster_management('halfMi_raster.tif;quarterMi_raster.tif;quartMi_Maintraster.tif;halfMi_Maintraster.tif;oneMi_Maintraster.tif',
                                   arcpy.env.workspace, 'mosaicBuffer_5c.tif',coordSys,'32_BIT_SIGNED', '5','1', "SUM", "FIRST")

#Where overlapping occurs, the higher end of the lower input range is inclusive, 
#and the lower end of the higher input range is exclusive.
# e.g. reclassifying values 1 to 5 as 100 and values 5 to 10 as 200, an input value less than or equal to 5 will be assigned the value 100

outReclass = Reclassify('mosaicBuffer_5c.tif', "Value",RemapRange([[1,2,5],[2,11,4],[11,201,3],[201,1112,2],[1112,111111,1]]), "NODATA")
outReclass = Reclassify('mosaicBuffer_5c.tif', "Value",
                        RemapRange([[1,2,6],[2,11,5],[100,100,'NODATA'],[101,110,4],[110,201,3],[201,1112,2],[1112,111111,1]]), "NODATA")

outReclass.save("MergeReclass_5c3.tif")
############################################################
Delete=False
if True:
    fileToDelete = [MaintBuffer_quart, MaintBuffer_half, FullBuffer_quartmi, \
                    FullBuffer_halfmi, 'halfMi_raster.tif', 'quarterMi_raster.tif',\
                    'quartMi_Maintraster.tif', 'halfMi_Maintraster.tif', \
                    'AddedBufRas.tif', 'merged.shp']
    
    for f in fileToDelete:
        try:
            arcpy.Delete_management(f)
        except:
            try:
                arcpy.Delete_management(os.path.join(arcpy.env.workspace, f))
            except:
                print ('Some error when deleting file:',f)
            
############################################################
#quarter mi trail buffer from maintained trails = 10

