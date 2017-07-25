import arcpy
import os
import datetime
from arcpy.sa import Slope, RemapRange, Reclassify

def create_unique_fgdb(workspace):
    print ("creating workspace file geodatabase...")
    timestamp = '{:%Y%m%d_%H%M}'.format(datetime.datetime.now())
    workspace_gdb_name = "Buffer_{0}".format(timestamp)
    workspace_gdb = arcpy.CreateFileGDB_management(workspace,
                                                   workspace_gdb_name).getOutput(0)
    return workspace_gdb

def cleanup_trash(cleanup_list):
    """

    :param cleanup_list:
    :return:
    """
    print ("cleaning up files...")
    for items in cleanup_list:
        arcpy.Delete_management(items)
    print ("done cleaning up files")


def get_fc_name_from_full_path(fc_path):
    """

    :param fc_path:
    :return:
    """
    return fc_path.split("\\")[-1]

def convert_polygon_to_raster(workspace_gdb, in_feature, value, out_raster_name):
    print ("executing convert polygon to raster...")
    output_path = os.path.join(workspace_gdb, out_raster_name)
    output_raster = arcpy.PolygonToRaster_conversion(in_feature, value, output_path).getOutput(0)
    print ("created output raster at {0}".format(output_raster))
    print ("finished processing conversion")
    return output_raster

def create_security_raster(workspace_gdb,
                           in_features_list,
                           buffer_size,
                           buffer_attribute,
                           clip_to,
                           clean_up_temp_files=True):
    """
    
    :param clean_up_temp_files: create a trash bucket
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
        work_buffer_out = arcpy.Buffer_analysis(item_to_buffer,
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
    # Convert to raster
    value = "OBJECTID"
    out_raster_name = "security_raster"
    out_raster = convert_polygon_to_raster(workspace_gdb, dissolvedBuffers, value, out_raster_name)


    # Step 6
    if clean_up_temp_files == True:
        cleanup_trash(trash_bucket)

    print ("end of security buffer script")
    return out_raster

def create_slope_raster(workspace_gdb,
                        input_elevation,
                        output_measurement,
                        z_factor):
    arcpy.CheckOutExtension("Spatial")
    output_slope_raster = Slope(input_elevation,
                                output_measurement,
                                z_factor)
    slope_raster = os.path.join(workspace_gdb, "slope_raster")
    output_slope_raster.save(slope_raster)

    print ("end of slope script")
    return slope_raster

def calculate_statistics(in_raster_dataset):
    arcpy.CalculateStatistics_management(in_raster_dataset)


def make_raster_layer(workspace_gdb,
                      in_raster,
                      out_raster_layer,
                      where_clause,
                      envelope,
                      band_index):
    # os.path.join(workspace_gdb, "Reclass_slop1")
    #
    # arcpy.MakeRasterLayer_management(in_raster,
    #                                  out_raster_layer,
    #                                  where_clause,
    #                                  envelope,
    #                                  band_index).getOutput(0)

    output_make_layer = arcpy.MakeRasterLayer_management(in_raster,
                                                     out_raster_layer,
                                                     where_clause,
                                                     envelope,
                                                     band_index).getOutput(0)

    # Reclass_slop1 = os.path.join(workspace_gdb, "Reclass_slop1")
    output_make_layer.save("MakeRas_slope_r1")
    return output_make_layer

def reclassify_raster_layer(workspace_gdb,
                            in_raster_layer,
                            reclass_field,
                            remap,
                            missing_values):
    work_reclass_output = arcpy.sa.Reclassify(in_raster_layer,
                                              reclass_field,
                                              remap,
                                              missing_values)

    reclass_output = os.path.join(workspace_gdb, "reclass_output")
    work_reclass_output.save(reclass_output)
    print ("end of reclassify")
    return reclass_output






# def buffer_clip_protected_areas(workspace_gdb,
#                                 input_protected_areas,
#                                 pa_buffer_size,
#                                 pa_buffer_attribute,
#                                 clipTo,
#                                 clean_up_temp_files=True):
