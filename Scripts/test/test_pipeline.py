''' Runs unit tests for Util functionality '''
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))


import unittest
from main.consolidate_uber_data import GeomParser


class PieplineTests(unittest.TestCase):
    def test_csv_list(self):
        self.assertEqual(len(GeomParser().get_list_of_uber_csv_paths()), 7)