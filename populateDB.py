#from models import *
from app import app, db
import pandas as pd
import sqlalchemy as sa
import xml.etree.ElementTree as ET

def initialise_database():

    #reads the csv files to import the data
    zipcode_data = pd.read_csv('datasets/zipcode_info_normalised.csv').drop('Unnamed: 0', axis = 1)
    crime_data = pd.read_csv('datasets/2017_crime_data.csv').drop('Unnamed: 0', axis = 1)
    weather_data = pd.read_csv('datasets/2017_weather_data.csv').drop('Unnamed: 0', axis = 1)
    zipcodes_boundaries = pd.read_csv('datasets/zipcodes_boundaries.csv')

    #used to import the dataframe data into database
    con = sa.create_engine(app.config['SQLALCHEMY_DATABASE_URI'])

    #add for each of the zipcodes in the table the boundary from the dataframe
    zipcode_data = (pd.merge(zipcode_data, zipcodes_boundaries, left_on=['zipcode'], right_on=['ZIP'])).drop(['ZIP'], axis = 1)
    zipcode_data['geometry'] = zipcode_data['geometry'].apply(getCoordinates)
    zipcode_data['geometry'] = zipcode_data['geometry'].astype(str)

    #populating the tables from the dataframes
    zipcode_data.to_sql(name='zipcode', if_exists='replace', index=False, con=con)
    crime_data.to_sql(name='crime_data', if_exists='replace', index=False, con=con)
    weather_data.to_sql(name='weather', if_exists='replace', index=False, con=con)


#gets coordinates of the zipcode boundary from KML text
def getCoordinates(s):
    root = ET.fromstring(s)
    if(root.tag == 'Polygon'):
        coordString = root[0][0][0].text
    else:
        coordString = root[0][0][0][0].text
    #print(coordString)
    coordSets = coordString.split(' ')
    longs = []
    lats = []
    res = []
    for c in coordSets:
        coords = c.split(',')
        longs.append(coords[0])
        lats.append(coords[1])
    for la, lo in zip(lats, longs):
        coord = {"lat": float(la), "lng": float(lo)}
        print(coord)
        res.append(coord)
    print(res)
    return res

