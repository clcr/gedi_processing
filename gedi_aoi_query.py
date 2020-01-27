import h5py
import geopandas as gp
import pandas as pd
import geopandas
import matplotlib.pyplot as plt

import os
import argparse

parser = argparse.ArgumentParser(description="Collectes all points within aoi from the gedi dataset")
parser.add_argument('gedi_dir', help = "Path to the directory containing gedi data")
parser.add_argument("out_path", help = "Path to the output file")
parser.add_argument("aoi_path", help = "Path to a shapefile or geojson containing an aoi")
args = parser.parse_args()

gedi_file_list = [os.path.join(args.gedi_dir, file_name) 
                    for file_name
                    in os.listdir(args.gedi_dir)
                    if file_name.endswith('.h5')]
gedi_file_list.sort()

aoi_overlay = gp.read_file(args.aoi_path)

gdf_list = []

for gedi_file in gedi_file_list:
        gedi_swath = h5py.File(gedi_file, 'r')
        for beam in gedi_swath.values():
            try:
                lats = beam["geolocation"]["latitude_bin0"]
                lons = beam["geolocation"]["longitude_bin0"]
                pai = beam["pai"]
                df = pd.DataFrame({'pai':pai,
                                   'height':beam['rh100'],
                                   'beam':beam['beam'],
                                   'Latitude':lats,
                                   'Longitude':lons
                                  })
                gdf = gp.GeoDataFrame(df, geometry = gp.points_from_xy(df.Longitude, df.Latitude))
                filtered_gdf = gdf[gdf.geometry.within(aoi_overlay.geometry[0])]
                gdf_list.append(filtered_gdf)
            except KeyError:
                print("Geolocation not found for beam thingy, continuing")
            continue

	
final_gdf = pd.concat(gdf_list)
final_gdf.to_file(args.out_path)

