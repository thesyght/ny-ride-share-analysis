''' Runs unit tests for Util functionality '''
import csv
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from shapely.geometry import Polygon, MultiPolygon
from shapely import wkt

import unittest
from main.consolidate_uber_data import UberTripCSVReader, NYCBoroughKMLReader


class ReaderTests(unittest.TestCase):
    def test_csv_reader_file_read(self):
        file_path = '/home/tys/Documents/MLpipeline/Experiments/ny-ride-share-analysis/Data/uber-trip-data/uber-raw-data-apr14.csv'
        csv_reader = UberTripCSVReader(file_path)
        self.assertGreaterEqual(len(csv_reader.get_csv_contents()), 1)

    def test_kml_reader_file_read(self):
        file_path = '/home/tys/Documents/MLpipeline/Experiments/ny-ride-share-analysis/Data/NYC_Borough_Boundaries.kml'
        kml_reader = NYCBoroughKMLReader(file_path)
        kml_reader.read_kml()
        self.assertEqual(len(kml_reader.get_borough_names()), 5)
    
    def test_kml_reader_polygon_from_string(self):
        cordinates = ['-73.89680883223778 40.79580844515979', '-73.89693872998787 40.79563587285361', '-73.89723603843935 40.79572003753713', '-73.89796839783742 40.795644839161994', '-73.89857332665562 40.7960691402596', '-73.89895261832532 40.796227852579634', '-73.89919434249981 40.79650245601826', '-73.89852052071454 40.79693619418981', '-73.8978825324018 40.79711653214705', '-73.89713149795635 40.79679807772831', '-73.89678526341234 40.796329166487105', '-73.89680883223778 40.79580844515979']
        kml_reader = NYCBoroughKMLReader('/')
        polygon = kml_reader.convert_list_of_string_cordinates_into_polygon(cord_list=cordinates)
        self.assertIsInstance(polygon, Polygon)
        self.assertFalse(polygon.is_empty)
        mulitpolygon = kml_reader.convert_list_of_polygons_into_multipolygon([polygon])
        self.assertIsInstance(mulitpolygon, MultiPolygon)
        self.assertFalse(mulitpolygon.is_empty)
        
    
    def test_point_in_polygon(self):
        polygon = wkt.loads('POLYGON((-73.89680883223778 40.79580844515979, -73.89693872998787 40.79563587285361, -73.89723603843935 40.79572003753713, -73.89796839783742 40.795644839161994, -73.89857332665562 40.7960691402596, -73.89895261832532 40.796227852579634, -73.89919434249981 40.79650245601826, -73.89852052071454 40.79693619418981, -73.8978825324018 40.79711653214705, -73.89713149795635 40.79679807772831, -73.89678526341234 40.796329166487105, -73.89680883223778 40.79580844515979))')
        point = wkt.loads('POINT(-73.8978982 40.7963994)')
        csv_reader = UberTripCSVReader('/')
        self.assertTrue(csv_reader.check_if_point_inside_polygon(point, polygon))
