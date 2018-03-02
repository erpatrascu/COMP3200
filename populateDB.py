#from models import *
from app import app, db
import pandas as pd
import sqlalchemy as sa


def initialise_database():
    zipcode_data = pd.read_csv('datasets/zipcodes_info.csv').drop('Unnamed: 0', axis = 1)
    crime_data = pd.read_csv('datasets/2017_crime_data.csv').drop('Unnamed: 0', axis = 1)
    weather_data = pd.read_csv('datasets/2017_weather_data.csv').drop('Unnamed: 0', axis = 1)

    con = sa.create_engine(app.config['SQLALCHEMY_DATABASE_URI'])
    zipcode_data.to_sql(name='zipcode', if_exists='append', index=False, con=con)
    crime_data.to_sql(name='crime_data', if_exists='append', index=False, con=con)
    weather_data.to_sql(name='weather', if_exists='append', index=False, con=con)


