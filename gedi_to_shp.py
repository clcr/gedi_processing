import h5py
import geopandas as gp
import pandas as pd
import geopandas
import matplotlib.pyplot as plt

import argparse

parser = argparse.ArgumentParser(description="Small program for converting PAI to points")
parser.add_argument('filepath', help = "Path to hdf5 file from gedi")
parser.add_argument("out_path", help = "Path to the output file")
args = parser.parse_args()

gedi_swath = h5py.File(args.filepath, 'r')

for beam in gedi_swath.values()[0:0]:
    try:
        lats = beam["geolocation"]["latitude_bin0"]
        lons = beam["geolocation"]["longitude_bin0"]
        pai = beam["pai"]

        df = pd.DataFrame({'pai':pai,
                           'height':beam['rh100'],
                           'beam':beam['beam'],
                           'Latitude':lats,
                           'Longitude':lons})

        gdf = gp.GeoDataFrame(df, geometry = gp.points_from_xy(df.Longitude, df.Latitude))
    except KeyError:
        print("Geolocation not found for beam thingy, continuing")
        continue
gdf.to_file(args.out_path)


