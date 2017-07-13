import arcpy
import os
import datetime
from arcpy.sa import Slope, RemapRange, Reclassify


def cleanup_trash(cleanup_list):
    """

    :param cleanup_list:
    :return:
    """
    print ("cleaning up files...")
    for items in cleanup_list:
        arcpy.Delete_management(cleanup_list)
    print ("done cleaning up files")



def convert_polygon_to_raster(in_feature, value, out_raster):
    print ("executing convert polygon to raster...")
    output_raster = arcpy.PolygonToRaster_conversion(in_feature, value, out_raster).getOutput(0)
    print ("created output raster at {0}".format(output_raster))
    print ("finished processing conversion")
    return output_raster



def create_security_raster(workspace_gdb, in_features_list,
                           buffer_size,
                           buffer_attribute,
                           clip_to,
                           clean_up_temp_files=True):
    """
    
    :param in_features_list: input points, lines, or polygons to be buffered
    :param buffer_size: specify numerical buffer distance
    :param buffer_attribute: specify distance units
    :param clip_to: input boundary to clip buffer to 
    :return: raster 
    """

    trash_bucket = []

    # Set a few variables for the iterative buffer operation
    buffer_size_string = "{0} {1}".format(buffer_size, buffer_attribute)
    counter = 0
    temp_output_list = []

    # Iterate on each input in the items_to_buffer list to run a buffer
    for item_to_buffer in in_features_list:
        counter += 1
        # Specify a temporary path to the buffer output
        work_buffer_out_path = os.path.join(workspace_gdb, "buffer_" + str(counter))
        # Run the arcpy buffer tool
        work_buffer_out = arcpy.Buffer_analysis(in_features_list,
                                                work_buffer_out_path,
                                                buffer_size_string).getOutput(0)
        # Add our output buffer to the temp output buffer container
        temp_output_list.append(work_buffer_out)
        trash_bucket.append(work_buffer_out)

    # Step 2

    print ("merging the output buffers...")
    # Convert list of buffer output paths to a semicolon delimited string
    bufferList = "; ".join(temp_output_list)

    # Execute Merge
    mergedBuffers = os.path.join(workspace_gdb, "mergedBuffers")
    arcpy.Merge_management(bufferList, mergedBuffers)
    trash_bucket.append(mergedBuffers)

    # Step 3

    print ("clipping merged buffer layer...")
    # Clip merged layers to country boundary
    clippedMerge = os.path.join(workspace_gdb, "clippedMerge")
    arcpy.Clip_analysis(mergedBuffers, clip_to, clippedMerge)
    trash_bucket.append(clippedMerge)

    # Step 4

    print ("dissolving...")
    # Execute Dissolve
    dissolvedBuffers = os.path.join(workspace_gdb, "dissolvedBuffers")
    arcpy.Dissolve_management(clippedMerge, dissolvedBuffers)
    trash_bucket.append(dissolvedBuffers)

    # Step 5

    print ("converting to raster...")
    # Set local variables
    in_features = dissolvedBuffers
    value_field = "OBJECTID"
    out_raster = os.path.join(workspace_gdb, "security_raster")
    # Execute PolygonToRaster
    arcpy.PolygonToRaster_conversion(in_features, value_field, out_raster)

    if clean_up_temp_files:
        cleanup_trash(trash_bucket)


    print ("end of security buffer script")
    return out_raster



