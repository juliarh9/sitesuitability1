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
input_elevation = r"C:\Users\juli9202\Documents\2017_06\Site Suitability Analysis Model\Data\dem_250m"

floodplains_value = "LITH_ID"
wetlands_value = "WETLAND"
soils_value = "SDRA"
input_floodplains = r"C:\Users\juli9202\Documents\2017_06\Site Suitability Analysis Model\Data\ke_floodplains.shp"
input_wetlands = r"C:\Users\juli9202\Documents\2017_06\Site Suitability Analysis Model\Data\wetlands\ke_wetlands.shp"
input_soils = r"C:\Users\juli9202\Documents\2017_06\Site Suitability Analysis Model\Data\soils.shp"



workspace_gdb = sitesuitability_utils.create_unique_fgdb(workspace)

work_input_list = [input_military_installations,
                   input_areas_of_conflict,
                   input_administrative_boundary]

print("Creating Security Raster...")
slope_raster_output = sitesuitability_utils.create_security_raster(workspace_gdb,
                                                                   work_input_list,
                                                                   buffer_size,
                                                                   buffer_attribute,
                                                                   clipTo)
print slope_raster_output

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

sitesuitability_utils.cleanup_trash()