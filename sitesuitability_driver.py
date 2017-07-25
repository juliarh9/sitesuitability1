import arcpy
import os
import datetime
from arcpy.sa import Slope, RemapRange, Reclassify
import sitesuitability_utils

# This is a driver that uses utilities from sitesuitability_utils module to execute against defined inputs
workspace = r"C:\Users\juli9202\Documents\2017_06\Site Suitability Analysis Model\ModelBuildertoPython\Work"
input_military_installations = r"C:\Users\juli9202\Documents\2017_06\Site Suitability Analysis Model\Data\militaryinstallations.shp"
input_areas_of_conflict = r"C:\Users\juli9202\Documents\2017_06\Site Suitability Analysis Model\Data\Conflicts2015.shp"
input_administrative_boundary = r"C:\Users\juli9202\Documents\2017_06\Site Suitability Analysis Model\Data\lineboundary.shp"
clipTo = r"C:\Users\juli9202\Documents\2017_06\Site Suitability Analysis Model\Data\ke_district_boundaries.shp"
buffer_size = 50
buffer_attribute = "kilometers"
floodplains_value = "LITH_ID"
wetlands_value = "WETLAND"
soils_value = "SDRA"
input_floodplains = r"C:\Users\juli9202\Documents\2017_06\Site Suitability Analysis Model\Data\ke_floodplains.shp"
input_wetlands = r"C:\Users\juli9202\Documents\2017_06\Site Suitability Analysis Model\Data\wetlands\ke_wetlands.shp"
input_soils = r"C:\Users\juli9202\Documents\2017_06\Site Suitability Analysis Model\Data\soils.shp"
input_elevation = r"C:\Users\juli9202\Documents\2017_06\Site Suitability Analysis Model\Data\dem_250m"
output_measurement = "PERCENT_RISE"
z_factor = "1"
out_rasterLayer = "MakeRas_slope_r1"
where_clause = None
envelope = "821686.139217557 -607944.542416126 1777512.22600888 654107.338987966"
band_index = None
reclass_field = "VALUE"
remap = "0 1 8;1 2 9;2 4 10;4 5 9;5 6 8;6 7 7;7 8 6;8 9 5;9 10 4;10 300 1"
missing_values = "NODATA"
input_bare_areas = r"C:\Users\juli9202\Documents\2017_06\Site Suitability Analysis Model\Data\ke_bareareas.shp"
bare_areas_value = "LCID"

workspace_gdb = sitesuitability_utils.create_unique_fgdb(workspace)

work_input_list = [input_military_installations,
                   input_areas_of_conflict,
                   input_administrative_boundary]

print("Creating Security Raster...")
security_raster_output = sitesuitability_utils.create_security_raster(workspace_gdb,
                                                                   work_input_list,
                                                                   buffer_size,
                                                                   buffer_attribute,
                                                                   clipTo, True)

print security_raster_output

print("Converting floodplains...")
floodplains_raster_output = sitesuitability_utils.convert_polygon_to_raster(workspace_gdb,
                                                                            input_floodplains,
                                                                            floodplains_value,
                                                                            "floodplains_raster")
print floodplains_raster_output

print ("Converting wetlands...")
wetlands_raster_output = sitesuitability_utils.convert_polygon_to_raster(workspace_gdb,
                                                                         input_wetlands,
                                                                         wetlands_value,
                                                                         "wetlands_raster")
print wetlands_raster_output

print ("Converting soils...")
soils_raster_output = sitesuitability_utils.convert_polygon_to_raster(workspace_gdb,
                                                                      input_soils,
                                                                      soils_value,
                                                                      "soils_raster")
print soils_raster_output

print ("Running slope...")
slope_raster_output = sitesuitability_utils.create_slope_raster(workspace_gdb,
                                                                input_elevation,
                                                                output_measurement,
                                                                z_factor)
print slope_raster_output


print ("Calculating statistics...")
calc_stat_output = sitesuitability_utils.calculate_statistics(slope_raster_output)

print ("Making raster layer...")
raster_layer_output = sitesuitability_utils.make_raster_layer(workspace_gdb,
                                                              slope_raster_output,
                                                              out_rasterLayer,
                                                              where_clause,
                                                              envelope,
                                                              band_index)
print raster_layer_output

print ("Reclassifying...")
reclassify_output = sitesuitability_utils.Reclassify(raster_layer_output,
                                                     reclass_field,
                                                     remap,
                                                     missing_values)
print reclassify_output

# print ("Converting bare areas...")
# bare_areas_raster_output = sitesuitability_utils.convert_polygon_to_raster(workspace_gdb,
#                                                                            input_bare_areas,
#                                                                            bare_areas_value,
#                                                                            "bare_areas_raster")



