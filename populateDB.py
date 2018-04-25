from app import app, db
import pandas as pd
import sqlalchemy as sa
from uszipcode import ZipcodeSearchEngine
import numpy as np
import datetime
from sklearn import preprocessing
import xml.etree.ElementTree as ET


def initialise_database():

    #reads the csv files to import the data
    zipcode_data = pd.read_csv('datasets/app_zipcode_data.csv').drop('Unnamed: 0', axis = 1)
    crime_data = pd.read_csv('datasets/app_crime_data.csv').drop('Unnamed: 0', axis = 1)

    weather_data = pd.read_csv('datasets/app_weather_data.csv').drop('Unnamed: 0', axis = 1)
    zipcodes_boundaries = pd.read_csv('datasets/zipcodes_boundaries.csv')

    #used to import the dataframe data into database
    con = sa.create_engine(app.config['SQLALCHEMY_DATABASE_URI'])

    #add for each of the zipcodes in the table the boundary from the dataframe
    zipcode_data = (pd.merge(zipcode_data, zipcodes_boundaries, left_on=['zipcode'], right_on=['ZIP'])).drop(['ZIP'], axis = 1)
    zipcode_data['geometry'] = zipcode_data['geometry'].apply(getCoordinates)
    zipcode_data['geometry'] = zipcode_data['geometry'].astype(str)

    import models

    #c1 = models.CrimeType("Violent Crime")
    #c2 = models.CrimeType("Burglary")
    #db.session.add(c1)
    #db.session.add(c2)
    #db.session.commit()

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
        res.append(coord)
    return res

#adding crime data to the database
def add_crime_data_to_DB():
    crimes_cut = import_crime_data()
    vcrime = crimes_cut.loc[
        crimes_cut['crime_code'].isin(['210', '220', '230', '231', '623', '624', '110', '120', '121'])]
    burglary = crimes_cut.loc[crimes_cut['crime_code'].isin(['310', '320'])]

    # used to import the dataframe data into database
    con = sa.create_engine(app.config['SQLALCHEMY_DATABASE_URI'])

    data = import_crime_type(vcrime, 1)
    data.to_sql(name='crime_data', if_exists='replace', index=False, con=con)

    data = import_crime_type(burglary, 2)
    data.to_sql(name='crime_data', if_exists='append', index=False, con=con)


#preprocess the imported data
def import_crime_data():
    #TODO reading the data in -> this will be changed
    crimes_raw = pd.read_csv("Crime_Data_from_2010_to_Present.csv", parse_dates=[2])

    # selecting only the columns we will be interested in
    crimes_cut = crimes_raw[['Date Occurred', 'Time Occurred', 'Crime Code', 'Location ']]

    # renaming the columns
    crimes_cut.rename(
        columns={'Date Occurred': 'date', 'Time Occurred': 'time', 'Crime Code': 'crime_code', 'Location ': 'location'},
        inplace=True)

    # getting the data from the last two years
    dates_filter = (crimes_cut['date'] > '2015-12-31') & (crimes_cut['date'] < '2018-06-01')
    crimes_cut = crimes_cut[dates_filter]

    #getting the data for certain crime codes (in this case violent crime and burglaries)
    crimes_cut = crimes_cut.loc[
        crimes_cut['crime_code'].isin(['210', '220', '230', '231', '623', '624', '110', '120', '121', '310', '320'])];

    #changing values of time feature
    crimes_cut['time'] = (crimes_cut['time']/100).astype(int)
    crimes_cut.is_copy = False

    # creating categories for the hours (by 8 hour groups)
    crimes_cut.loc[(crimes_cut['time'] >= 0) & (crimes_cut['time'] < 8), 'time'] = 0
    crimes_cut.loc[(crimes_cut['time'] >= 8) & (crimes_cut['time'] < 16), 'time'] = 1
    crimes_cut.loc[(crimes_cut['time'] >= 16) & (crimes_cut['time'] < 24), 'time'] = 2

    # creating latitude and longitude columns
    crimes_cut[['latitude', 'longitude']] = crimes_cut['location'].str.split(',\s+', expand=True)
    crimes_cut['latitude'] = crimes_cut['latitude'].str.replace("(", '').astype(float)
    crimes_cut['longitude'] = crimes_cut['longitude'].str.replace(")", '').astype(float)
    crimes_cut = crimes_cut.drop(['location'], axis=1)

    # get the zipcodes based on coordinates
    search = ZipcodeSearchEngine()

    # deleting the records that have null values or 0 in the relevant columns
    crimes_cut = crimes_cut.dropna(subset=['date', 'time', 'crime_code', 'latitude', 'longitude'])
    crimes_cut = crimes_cut[(crimes_cut['latitude'] != 0) & (crimes_cut['longitude'] != 0)]

    codes = [(search.by_coordinate(lat, lng, returns = 1))[0].Zipcode for lat, lng in zip(crimes_cut['latitude'], crimes_cut['longitude'])]
    crimes_cut['zipcode'] = codes

    return crimes_cut


#create a dataset that contains all the combinations of zipcode, date and time
def df_crossjoin(df1, df2, **kwargs):
    df1['_tmpkey'] = 1
    df2['_tmpkey'] = 1

    res = pd.merge(df1, df2, on='_tmpkey', **kwargs).drop('_tmpkey', axis=1)
    #res.index = pd.MultiIndex.from_product((df1.index, df2.index))

    df1.drop('_tmpkey', axis=1, inplace=True)
    df2.drop('_tmpkey', axis=1, inplace=True)

    return res

# add to the database the crime data by crime type
def import_crime_type(df, type):
    # counting the crimes by zipcode, date and time range
    counts = pd.DataFrame({'count': df.groupby(['zipcode', 'date', 'time']).size()}).reset_index()

    dfzipcode = pd.DataFrame({'zipcode' : df['zipcode'].unique()}).sort_values(by = 'zipcode')
    dfdate = pd.DataFrame({'date' : df['date'].unique()}).sort_values(by = 'date')
    dftime =  pd.DataFrame({'time' : df['time'].unique()}).sort_values(by = 'time')
    dfx = df_crossjoin(dfzipcode, dfdate, suffixes=('_orig', '_dest'))
    aux = df_crossjoin(dfx, dftime, suffixes=('_orig', '_dest'))

    # create a dataset that contains all the combinations of zipcode, date and time
    data = pd.merge(aux, counts, on=['zipcode', 'date', 'time'], how='outer')
    data['count'].fillna(0, inplace=True)

    #adding a column with year and month as it is needed for countings
    data['year_month'] = data['date'].map(lambda x: 100 * x.year + x.month)

    data.rename(columns={'count': 'vcrime'}, inplace=True)

    temp = count_by_loc(data)
    temp_time = count_by_loc_time(data)
    temp_t = count_by_time(data)

    # merging into the train dataset to contain the number of robberies happened the previous month, and the previous 6 months
    data = pd.merge(data, temp, on=['zipcode', 'year_month'])

    # merging into the train dataset to contain the number of robberies happened at different times the previous 6 months
    data = pd.merge(data, temp_time, on=['zipcode', 'year_month', 'time'])

    # merging into the train dataset to contain the number of robberies happened at different times the previous 6 months
    data = pd.merge(data, temp_t, on=['year_month', 'time'])

    #TODO: take the data from databasse
    zipcodes = pd.read_csv("app_zipcode_data.csv")
    zipcodes = zipcodes[["zipcode", "population"]]

    #changing the type from object to int and then merge with data
    data['zipcode'] = data['zipcode'].astype('int')

    data = pd.merge(data, zipcodes, on='zipcode')

    #for normalising the data values
    scaler = preprocessing.MinMaxScaler()
    scaled_data = scaler.fit_transform(data.loc[:, ['count_1m_loc', 'count_6m_loc', 'count_2y_loc',
                                                    'count_1m_loc_time', 'count_6m_loc_time', 'count_2y_loc_time',
                                                    'count_1m_time', 'count_6m_time', 'count_2y_time',
                                                    ]])
    scaled_data = pd.DataFrame(scaled_data, columns=['count_1m_loc', 'count_6m_loc', 'count_2y_loc',
                                                     'count_1m_loc_time', 'count_6m_loc_time', 'count_2y_loc_time',
                                                     'count_1m_time', 'count_6m_time', 'count_2y_time',
                                                     ])

    data = data.reset_index().drop('index', axis=1)
    data.loc[:,
    ['count_1m_loc', 'count_6m_loc', 'count_2y_loc', 'count_1m_loc_time', 'count_6m_loc_time', 'count_2y_loc_time',
     'count_1m_time', 'count_6m_time', 'count_2y_time']] = scaled_data.loc[:,
                                                           ['count_1m_loc', 'count_6m_loc', 'count_2y_loc',
                                                            'count_1m_loc_time', 'count_6m_loc_time',
                                                            'count_2y_loc_time',
                                                            'count_1m_time', 'count_6m_time', 'count_2y_time',
                                                            ]]

    #to only extract this months details
    now = datetime.datetime.now()
    date = 100 * now.year + now.month

    data = data[data['year_month'] == date]

    #creating an additional column
    data.loc[:,'crimes_per_pop'] = data['count_2y_loc']/data['population']
    data = data.replace(np.inf, 0)

    #dropping the unnecessary columns and the resulting duplicates
    data = data.drop(['date', 'vcrime', 'population'], axis=1)
    data = data.drop_duplicates()

    data.loc[:, 'crime_type'] = type

    scaled_data = scaler.fit_transform(data.loc[:, ['crimes_per_pop']])
    scaled_data = pd.DataFrame(scaled_data, columns=['crimes_per_pop'])
    data.loc[:, ['crimes_per_pop']] = scaled_data.loc[:, ['crimes_per_pop']]

    return data



# counting the robberies by zipcode that happened prev month, 6 months and 2 years
def count_by_loc(data):
    temp = data.groupby(['zipcode', 'year_month']).agg({'vcrime': 'sum'}).reset_index()
    temp['order_within_group'] = temp.groupby('zipcode').cumcount()

    temp['count_1m_loc'] = (temp.groupby('zipcode')['vcrime']
                            .apply(lambda x: pd.rolling_sum(x, window=1, min_periods=0)
                                   .shift()
                                   .fillna(0)))

    # counting the v crimes in the previous 6 months for each zipcode
    temp['count_6m_loc'] = (temp.groupby('zipcode')['vcrime']
                            .apply(lambda x: pd.rolling_sum(x, window=6, min_periods=0)
                                   .shift()
                                   .fillna(0)))

    temp['count_2y_loc'] = (temp.groupby('zipcode')['vcrime']
                            .apply(lambda x: pd.rolling_sum(x, window=24, min_periods=0)
                                   .shift()
                                   .fillna(0)))

    temp = temp.drop(['vcrime', 'order_within_group'], axis=1)
    return temp


# counting the robberies by zipcode, time and month in prev month, 6 months and 2 years
def count_by_loc_time(data):
    temp_time = data.groupby(['zipcode', 'time', 'year_month']).agg({'vcrime': 'sum'}).reset_index()
    temp_time['order_within_group'] = temp_time.groupby('zipcode').cumcount()

    temp_time['count_1m_loc_time'] = (temp_time.groupby(['zipcode', 'time'])['vcrime']
                                      .apply(lambda x: pd.rolling_sum(x, window=1, min_periods=0)
                                             .shift()
                                             .fillna(0)))

    # counting the robberies in the previous 6 months for each zipcode and time range
    temp_time['count_6m_loc_time'] = (temp_time.groupby(['zipcode', 'time'])['vcrime']
                                      .apply(lambda x: pd.rolling_sum(x, window=6, min_periods=0)
                                             .shift()
                                             .fillna(0)))

    temp_time['count_2y_loc_time'] = (temp_time.groupby(['zipcode', 'time'])['vcrime']
                                      .apply(lambda x: pd.rolling_sum(x, window=24, min_periods=0)
                                             .shift()
                                             .fillna(0)))
    # droping columns
    temp_time = temp_time.drop(['vcrime', 'order_within_group'], axis=1)

    return temp_time

# counting the robberies by time in prev month, 6 months and 2 years
def count_by_time(data):
    # counting the robberies by zipcode, time and month (used in computing the crimes happened the previous 6 months)
    temp_t = data.groupby(['time', 'year_month']).agg({'vcrime': 'sum'}).reset_index()
    # temp_t['order_within_group'] = temp_t.groupby('zipcode').cumcount()

    temp_t['count_1m_time'] = (temp_t.groupby(['time'])['vcrime']
                               .apply(lambda x: pd.rolling_sum(x, window=1, min_periods=0)
                                      .shift()
                                      .fillna(0)))

    # counting the robberies in the previous 6 months for each zipcode and time range
    temp_t['count_6m_time'] = (temp_t.groupby(['time'])['vcrime']
                               .apply(lambda x: pd.rolling_sum(x, window=6, min_periods=0)
                                      .shift()
                                      .fillna(0)))

    temp_t['count_2y_time'] = (temp_t.groupby(['time'])['vcrime']
                               .apply(lambda x: pd.rolling_sum(x, window=24, min_periods=0)
                                      .shift()
                                      .fillna(0)))
    # droping columns
    temp_t = temp_t.drop(['vcrime'], axis=1)

    return temp_t