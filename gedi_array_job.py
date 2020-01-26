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
args = parser.parse_args()

gedi_file_list = [os.path.join(args.gedi_dir, file_name) 
                    for file_name
                    in os.listdir(args.gedi_dir)
                    if file_name.endswith('.h5')]

gedi_file_list.sort()

index = int(os.getenv("PBS_ARRAYID"))
gedi_file = gedi_file_list[index]
gedi_file_name = gedi_file.rpartition('/')[2]
gedi_swath = h5py.File(gedi_file, 'r')
df_array = []
for beam in gedi_swath.values():
    try:
        lats = beam["geolocation"]["latitude_bin0"]
        lons = beam["geolocation"]["longitude_bin0"]
        pai = beam["pai"]

        df_array.append(pd.DataFrame({'pai':pai,
                           'beam':beam['beam'],
                           'Latitude':lats,
                           'Longitude':lons}))
    except KeyError:
        print("Geolocation not found for beam thingy, continuing")
        continue
df = pd.concat(df_array)
gdf = gp.GeoDataFrame(df, geometry = gp.points_from_xy(df.Longitude, df.Latitude))
shp_folder = os.path.join(args.out_dir, gedi_file_name)
try:
    os.mkdir(shp_folder)
except FileExistsError:
    pass
gdf.to_file(os.path.join(shp_folder, gedi_file_name + ".shp"))

