import h5py
import geopandas as gp
import pandas as pd
import geopandas
import matplotlib.pyplot as plt
from tempfile import TemporaryDirectory
import subprocess
import os
import argparse


def gedi_aoi_process(gedi_dir, out_path, aoi_path, product_list):
    """
    Produces a shapefile of every
    :param gedi_dir:
    :param out_path:
    :param aoi_path:
    :param feature_list:
    :return:
    """
    gedi_dir = os.path.abspath(gedi_dir)
    gedi_file_list = [os.path.join(gedi_dir, file_name)
                      for file_name
                      in os.listdir(gedi_dir)
                      if file_name.endswith('.h5')]
    gedi_file_list.sort()
    aoi_overlay = gp.read_file(aoi_path)
    gdf_list = []
    for gedi_file in gedi_file_list:
            print("Processing {}".format(gedi_file))
            gedi_swath = h5py.File(gedi_file, 'r')
            for beam in gedi_swath.values():
                try:
                    lats = beam["geolocation"]["latitude_bin0"]
                    lons = beam["geolocation"]["longitude_bin0"]
                    product_dict = {product: beam[product] for product in product_list}
                    product_dict.update({
                        'Latitude': lats,
                        'Longitude': lons
                    })
                    df = pd.DataFrame(product_dict)
                    gdf = gp.GeoDataFrame(df, geometry = gp.points_from_xy(df.Longitude, df.Latitude))
                    filtered_gdf = gdf[gdf.geometry.within(aoi_overlay.geometry[0])]
                    if len(filtered_gdf) == 0:
                        continue
                    gdf_list.append(filtered_gdf)
                except KeyError:
                    print("Key missing")
    final_gdf = pd.concat(gdf_list)
    with TemporaryDirectory() as td:
        # Geopandas writes to geojson quicker than it writes to .shp
        temp_geojson = os.path.join(td, "json")
        print("Creating temporary geojson at {}".format(temp_geojson))
        final_gdf.to_file(temp_geojson, driver="GeoJSON")
        print("Running ogr2ogr")
        subprocess.run(["ogr2ogr", "-f", "ESRI Shapefile", out_path, temp_geojson])


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Collectes all points within aoi from the gedi dataset and saves"
                                                 "to a shapefile with the specified data products as attributes")
    parser.add_argument('gedi_dir', help="Path to the directory containing gedi data")
    parser.add_argument("out_path", help="Path to the output file")
    parser.add_argument("aoi_path", help="Path to a shapefile or geojson containing an aoi")
    parser.add_argument("product_labels", help="IDs of features to place in points ")
    args = parser.parse_args()
    gedi_aoi_process(args.gedi_dir, args.out_path, args.aoi_path, args.product_labels)

