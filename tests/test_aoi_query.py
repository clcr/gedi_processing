import pytest
from gedi_processing.gedi_aoi_query import gedi_aoi_process
import os, pathlib

def setup_module():
    os.chdir(pathlib.Path(__file__).parent)

def test_gedi_aoi_process():
    gedi_aoi_process("test_data",
                     "test_outputs/test_aoi.shp",
                     "test_data/test_equator_aoi.geojson",
                     ["rh100", "pai", "cover", "beam"])
