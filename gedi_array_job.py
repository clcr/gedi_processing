import h5py
import geopandas as gp
import pandas as pd
import geopandas
import matplotlib.pyplot as plt
import os
import argparse

parser = argparse.ArgumentParser(description="Small program for converting PAI to points: ALICE array edition")
parser.add_argument('gedi_dir', help = "Path to dir containing gedi data")
parser.add_argument("out_dir", help = "Path to the output dir for shapefiles")

gedi_file_list = [os.path.join(args.gedi_dir, file_name) 
                    for file_name
                    in os.listdir(args.gedi_dir)
                    if file_name.endswith('.h5')].sort()

index = os.getenv("PBS_ARRAYID")
gedi_file = gedi_file_list[index])
gedi_file_name = gedi_file.rpart('/')[1]
gedi_swath = h5py.File(gedi_file, 'r')
for beam in gedi_swath.values():
    try:
        lats = beam["geolocation"]["latitude_bin0"]
        lons = beam["geolocation"]["longitude_bin0"]
        pai = beam["pai"]

        df = pd.DataFrame({'pai':pai,
                           'beam':beam['beam'],
                           'Latitude':lats,
                           'Longitude':lons})
        gdf = gp.GeoDataFrame(df, geometry = gp.points_from_xy(df.Longitude, df.Latitude))
    except KeyError:
        print("Geolocation not found for beam thingy, continuing")
        continue
shp_folder = os.mkdir(os.join(args.out_path, gedi_file_name))
gdf.to_file(os.join(shp_folder, gedi_file_name.shp))

