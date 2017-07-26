import arcpy
import os
import datetime
from arcpy.sa import Slope, RemapRange, Reclassify

print ("started operation")

### Security Buffer Model Script ###

### Pseudo-Code ###

# Step 0: Set the configuration and input parameters

# Step 1: Buffer each input

# Step 2: Merge the output buffers

# Step 3: Clip the merged output by the admin boundary

# Step 4: Dissolve output to prepare for polygon to raster conversion

# Step 5: Convert the dissolved buffers to a raster file for final output

# Step 6: Clean up intermediate files

#### TOOL PARAMETERS ####
print ("setting the workspace...")
workspace = arcpy.GetParameterAsText(0)
input_military_installations = arcpy.GetParameterAsText(1)
input_areas_of_conflict = arcpy.GetParameterAsText(2)
input_administrative_boundary = arcpy.GetParameterAsText(3)
buffer_size = arcpy.GetParameterAsText(4)
buffer_attribute = arcpy.GetParameterAsText(5)
clipTo = arcpy.GetParameterAsText(6)
input_elev_raster = arcpy.GetParameterAsText(7)
reclass_field = arcpy.GetParameterAsText(8)
input_floodplains = arcpy.GetParameterAsText(9)
floodplains_value = arcpy.GetParameterAsText(10)
input_wetlands = arcpy.GetParameterAsText(11)
wetlands_value = arcpy.GetParameterAsText(12)
input_soils = arcpy.GetParameterAsText(13)
soils_value = arcpy.GetParameterAsText(14)

#### END TOOL PARAMETERS ####


# Step 0

# Set workspace
# workspace = r""
# process_name = r""

# Create workspace file geodatabase
print ("creating workspace file geodatabase...")
timestamp = '{:%Y%m%d_%H%M}'.format(datetime.datetime.now())
workspace_gdb_name = "Buffer_{0}".format(timestamp)
workspace_gdb = arcpy.CreateFileGDB_management(workspace,
                                               workspace_gdb_name).getOutput(0)

# Set reference to the buffer tool operation config parameters
print ("setting reference to the buffer tool operation configuration parameters...")
buffer_size_string = "{0} {1}".format(buffer_size, buffer_attribute)

# Setting references to the inputs of the process
print ("setting references to the inputs of the process...")

# Step 1

print ("buffering inputs...")
# Create a list containing the items that need to be buffered
items_to_buffer = [input_military_installations,
                   input_areas_of_conflict,
                   input_administrative_boundary]

# Set a few variables for the iterative buffer operation
counter = 0
temp_output_list = []

# Iterate on each input in the items_to_buffer list to run a buffer
for item_to_buffer in items_to_buffer:
    counter += 1
    # Specify a temporary path to the buffer output
    work_buffer_out_path = os.path.join(workspace_gdb, "buffer_" + str(counter))
    # Run the arcpy buffer tool
    work_buffer_out = arcpy.Buffer_analysis(item_to_buffer,
                                            work_buffer_out_path,
                                            buffer_size_string).getOutput(0)
    # Add our output buffer to the temp output buffer container
    temp_output_list.append(work_buffer_out)

# Step 2

print ("merging the output buffers...")
# Convert list of buffer output paths to a semicolon delimited string
bufferList = "; ".join(temp_output_list)

# Execute Merge
mergedBuffers = os.path.join(workspace_gdb, "mergedBuffers")
arcpy.Merge_management(bufferList, mergedBuffers)

# Step 3

print ("clipping merged buffer layer...")
# Clip merged layers to country boundary
clippedMerge = os.path.join(workspace_gdb, "clippedMerge")
arcpy.Clip_analysis(mergedBuffers, clipTo, clippedMerge)

# Step 4

print ("dissolving...")
# Execute Dissolve
dissolvedBuffers = os.path.join(workspace_gdb, "dissolvedBuffers")
arcpy.Dissolve_management(clippedMerge, dissolvedBuffers)

# Step 5

print ("converting to raster...")
# Set local variables
in_features = dissolvedBuffers
value_field = "OBJECTID"
out_raster = os.path.join(workspace_gdb, "security_raster")
# Execute PolygonToRaster
arcpy.PolygonToRaster_conversion(in_features, value_field, out_raster)

# Step 6

print ("end of security buffer script")

###########################################################################################

### Topography Model ###

### Psuedo-Code ###

# Step 7: Set the configuration and input parameters

# Step 8: Execute slope tool on input elevation data

# Step 9: Calculate statistics on output slope raster and reclassify

# Step 10: Convert floodplain polygon to raster file

# Step 11: Convert wetlands polygon to raster file

# Step 12: Convert soil polygon to raster file using SDRA as the value

# Step 13: Clean up intermediate files

###

print ("starting topography model script...")

# Step 7

# Set references to the slope and reclassify tool operation configuration parameters
print ("setting references to the slope tool operation configuration parameters...")
outMeasurement = "PERCENT_RISE"
zFactor = 1

# Step 8

print ("executing slope...")
# Check out the ArcGIS Spatial Analyst extension
arcpy.CheckOutExtension("Spatial")
# Execute slope tool
outSlope = Slope(input_elev_raster, outMeasurement, zFactor)
# Specify a temporary path to the slope output
work_slope_out_path = os.path.join(workspace_gdb, "slope_raster")
# Save the output slope raster
outSlope.save(work_slope_out_path)

print (work_slope_out_path)

# Step 9

# Set local variables
input_slope_raster = work_slope_out_path

print ("calculating statistics...")
arcpy.CalculateStatistics_management(work_slope_out_path)

print ("reclassifying the slope output...")
work_reclass_out_path = os.path.join(workspace_gdb, "Reclass_slop1")
# Making Raster Layer
rasterLayer = arcpy.MakeRasterLayer_management(input_slope_raster,
                                               "MakeRas_slope_r1",
                                               None,
                                               "821686.139217557 -607944.542416126 1777512.22600888 654107.338987966",
                                               None).getOutput(0)
# Reclassifying
out_raster = arcpy.sa.Reclassify(rasterLayer,
                                 "VALUE",
                                 "0 1 8;1 2 9;2 4 10;4 5 9;5 6 8;6 7 7;7 8 6;8 9 5;9 10 4;10 300 1",
                                 "NODATA")

out_raster.save(work_reclass_out_path)

print(rasterLayer)
print(out_raster)
print(work_reclass_out_path)


# Step 10

print ("converting floodplains polygon to raster...")
# Set local variables
# floodplains_value = "LITH_ID"
# Specify a path to the raster output
out_floodplains_raster = os.path.join(workspace_gdb, "floodplains_raster")
# Execute PolygonToRaster
arcpy.PolygonToRaster_conversion(input_floodplains, floodplains_value, out_floodplains_raster)

# Step 11

print("converting wetlands polygon to raster...")
# Set local variables
# wetlands_value = "WETLAND"
# Specify a path to the raster output
out_wetlands_raster = os.path.join(workspace_gdb, "wetlands_raster")
# Execute PolygonToRaster
arcpy.PolygonToRaster_conversion(input_wetlands, wetlands_value, out_wetlands_raster)

# Step 12

print ("converting soils polygon to raster")
# Set local variables
# soils_value = "SDRA"
# Specify a path to the raster output
out_soils_raster = os.path.join(workspace_gdb, "soils_raster")
# Execute PolygonToRaster
arcpy.PolygonToRaster_conversion(input_soils, soils_value, out_soils_raster)


# Step 13

print ("end of topography model script")

###########################################################################################

### Environment and Vegetation Model Script ###

### Pseudo-Code ###

# Step 14: Set reference to the buffer tool configuration and input parameters

# Step 15: Buffer Protected Areas

# Step 16: Clip protected areas buffer to country boundary

# Step 17: Convert clip output polygon to raster file

# Step 18: Convert bare areas polygon to raster file

# Step 19: Reclassify tree cover raster file

# Step 20: Clean up intermediate files

###

# # Step 14
#
# # Set reference to tool operation config parameters
# print ("setting reference to the buffer tool operation configuration parameters...")
# buffer_distance = "40 kilometers"
# distance_field = "Distance"
# sideType = "FULL"
# endType = "ROUND"
# dissolveType = "ALL"
# protectedAreasValue = "FID"
#
# # Set references to the inputs of the process
# print ("setting reference to the inputs of the process...")
# input_protected_areas = r"C:\Users\juli9202\Documents\2017_06\Site Suitability Analysis Model\Data\ke_protected-areas.shp"
#
#
# # Step 15
#
# print ("buffering protected areas...")
# # Specify a path to the buffer output
# out_protected_areas = os.path.join(workspace_gdb, "protected_areas_buffer")
# #Execute the buffer tool
# arcpy.Buffer_analysis(input_protected_areas, out_protected_areas, buffer_distance, sideType, endType, dissolveType)
#
# # Step 16
#
# print ("clipping protected areas...")
# # Specify input and output paths
# input_pa_buffer = out_protected_areas
# out_clip_protected_areas = os.path.join(workspace_gdb, "protected_areas_clip")
# # Execute clip tool
# arcpy.Clip_analysis(input_pa_buffer, clipTo, out_clip_protected_areas)
# #
# # Step 17
#
# print ("converting to raster file...")
# # Specify input and output paths
# input_pa_polygon = out_clip_protected_areas
# out_protected_areas_raster = os.path.join(workspace_gdb, "protected_areas_raster")
# #Execute PolygonToRaster
# arcpy.PolygonToRaster_conversion(input_pa_polygon, protectedAreasValue, out_protected_areas_raster)


print ("ended operation")
