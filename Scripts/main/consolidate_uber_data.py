''' Consolidate uber data into a single csv to be more easily processed by QGIS, to avoid congestion abstract the data into weekly and monthly chunks
    This pipeline is built using simple TDD, OOD and loose contract by design principles '''

import os
import csv
from datetime import datetime

import xml.etree.ElementTree as etree
from shapely import wkt
from shapely.geometry import Point, Polygon, MultiPolygon

# import mplleaflet


class CSVReader:
    '''Read in csv and convert to dictionary'''
    def __init__(self, csv_path):
        self.csv_path = csv_path
        self.csv_contents = []
    
    def read_csv(self):
        '''Read csv'''
        pass


class UberTripCSVReader(CSVReader):
    '''CSV reader specific to uber csvs '''
    def __init__(self, csv_path):
        super().__init__(csv_path)
        self.output_path = csv_path.replace('.csv', '(PRUNED).csv')
    
    def get_csv_contents(self):
        ''' Read in csv if not already done and then return '''
        if not self.csv_contents:
            self.read_csv()
        return self.csv_contents
    
    def read_csv(self):
        ''' Read uber trip data which contains datetime and associated lat/long of pickup and base of driver
            Requirements: - File must be given as absolute and exists
                          - The headers: ['Date/Time', 'Lat, Long, Base'] must be available '''
        assert os.path.abspath(self.csv_path) == self.csv_path
        assert os.path.exists(self.csv_path)
        known_headers = ['Date/Time', 'Lat', 'Lon', 'Base']
        with open(self.csv_path, 'r') as _file:
            reader = csv.DictReader(_file)
            for known_header in known_headers: assert known_header in reader.fieldnames 
            for row in reader:
                self.csv_contents += [{'Datetime': datetime.strptime(row['Date/Time'], '%m/%d/%Y %H:%M:%S'), 'Lat': row['Lat'], 'Lon': row['Lon'], 'Base': row['Base']}] # Really slow would replace with own parser
    
    def prune_csv_of_points_outside_polygon(self, polygon):
        ''' For a given polygon prune all rows with points outside '''
        new_contents = []
        i = True
        for row in self.csv_contents:
            if i:
                print(row)
                print(polygon)
                i = False
            new_contents += [row] if self.check_if_row_valid(row, polygon) else []
        self.csv_contents = new_contents
        print(len(self.csv_contents))

    def save_csv(self):
        ''' Save csv to disk '''
        with open(self.output_path, 'w+') as _file:
            headers = ['Date', 'Time', 'Lat', 'Lon']
            writer = csv.DictWriter(_file, fieldnames=headers)
            writer.writeheader()
            for row in self.csv_contents:
                writer.writerow({'Date': row['Datetime'].strftime("%d/%m/%Y"), 'Time': row['Datetime'].strftime("%H:%M:%S"), 'Lat': row['Lat'], 'Lon': row['Lon']})

    def check_if_row_valid(self, row, polygon):
        assert isinstance(polygon, MultiPolygon)
        point = wkt.loads('POINT ({} {})'.format(row['Lon'], row['Lat']))
        return self.check_if_point_inside_polygon(point, polygon)

    def check_if_point_inside_polygon(self, point, polygon):
        ''' Check if point on row was inside polygon '''
        return polygon.contains(point)
        # This is slow but dont have time to refactor to use geopandas

class KMLReader:
    ''' Read in KML file and save as polygon '''
    def __init__(self, kml_path):
        self.kml_path = kml_path
        self.kml_data = {}
    
    def read_kml(self):
        pass

class NYCBoroughKMLReader(KMLReader):
    ''' Specific reading of NYC Borough kml files '''
    def __init__(self, kml_path):
        super().__init__(kml_path=kml_path)
    
    def read_kml(self):
        ''' Read in kml with specific format for NYC boroughs '''
        assert os.path.abspath(self.kml_path) == self.kml_path
        assert os.path.exists(self.kml_path)
        kml_tree = etree.parse(self.kml_path)
        for _kml_boroughs in kml_tree.getroot().iter('Placemark'):
            for _kml_borough_metadata_group in _kml_boroughs.iter('ExtendedData'):
                for _kml_borough_metadata in _kml_borough_metadata_group.iter('Data'):
                    if _kml_borough_metadata.get('name') == 'boro_name':
                        borough_name = _kml_borough_metadata.find('value').text
                        self.kml_data[borough_name] = []
            for _kml_polygon in _kml_boroughs.iter('Polygon'):
                for _cord_pair in _kml_polygon.iter('coordinates'):
                    if ',' not in _cord_pair.text:
                        continue
                    cord_pairs_clean = [cord_pair.replace(' ', '').replace(',', ' ') for cord_pair in _cord_pair.text.split('\n') if cord_pair.replace(' ', '').replace(',', ' ') != '']
                    self.kml_data[borough_name] += [cord_pairs_clean]
    
    def get_borough_names(self):
        '''Get a list of borough names which is the key for the kml hash'''
        return list(self.kml_data)
    
    def get_borough_polygons(self, borough_name):
        '''Get the borough's polygons associated to name '''
        assert borough_name in list(self.kml_data)
        polygon_shapes = []
        for polygon_cords in self.kml_data[borough_name]:
            polygon_shapes += [self.convert_list_of_string_cordinates_into_polygon(polygon_cords)]
        return polygon_shapes
    
    def convert_list_of_polygons_into_multipolygon(self, polygons):
        ''' Multipolygon will make point matching easier to work with '''
        return MultiPolygon(polygons)
    
    def convert_list_of_string_cordinates_into_polygon(self, cord_list):
        ''' Convert the string cordinates into a polygon shape 
            format for cords = (x y)'''
        assert cord_list
        assert len(cord_list[0].split(' ')) == 2
        base_string = 'POLYGON (('
        for cord in cord_list:
            if base_string != 'POLYGON ((':
                base_string += ','
            x_cord = float(cord.split(' ')[0])
            y_cord = float(cord.split(' ')[1])
            base_string += '{x_cord} {y_cord}'.format(x_cord=x_cord, y_cord=y_cord)
        base_string += '))'
        return wkt.loads(base_string)


class GeomParser:
    ''' Class that can take geometry objects and filter/parse them given some directive '''
    def __init__(self):
        self.uber_data_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../Data/uber-trip-data'))
        self.consolidated_uber_data = {}
        self.nyc_gis_kml_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../Data/NYC_Borough_Boundaries.kml'))
        self.kmlReader = NYCBoroughKMLReader(kml_path=self.nyc_gis_kml_path)
        self.operational_borough_name = 'Bronx'

    def run(self):
        ''' Pipeline to read in uber data month by month and parse out only the points in the Bronx area '''
        self.kmlReader.read_kml()
        borough_polygon = self.kmlReader.get_borough_polygons(borough_name=self.operational_borough_name)
        operational_polygon = self.kmlReader.convert_list_of_polygons_into_multipolygon(borough_polygon)
        for uber_trip_csv_path in self.get_list_of_uber_csv_paths():
            csvReader = UberTripCSVReader(csv_path=uber_trip_csv_path)
            csvReader.read_csv()
            csvReader.prune_csv_of_points_outside_polygon(polygon=operational_polygon)
            csvReader.save_csv()

    def get_list_of_uber_csv_paths(self):
        assert os.path.exists(self.uber_data_path)
        uber_trip_csv_paths = [os.path.join(self.uber_data_path, fname) for fname in os.listdir(self.uber_data_path) if fname.endswith('.csv') and 'REFORMATED' not in fname and 'PRUNED' not in fname and 'uber-raw-data' in fname]
        uber_trip_csv_paths.sort()
        return uber_trip_csv_paths


if __name__ == '__main__':
    geomParser = GeomParser()
    geomParser.run()
    
