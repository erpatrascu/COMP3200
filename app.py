# app.py
from flask import Flask, request, render_template, jsonify
from flask_sqlalchemy import SQLAlchemy
import pickle
import pandas as pd
from weather import Weather, Unit
from sklearn import preprocessing
import calendar
import datetime
import tempfile

app = Flask(__name__)

#configuring the database
POSTGRES = {
    'user': 'erp3g15',
    'pw': 'password',
    'db': 'crimedb',
    'host': 'localhost',
    'port': '5432',
}

app.config['DEBUG'] = True
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False # silence the deprecation warning
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql+psycopg2://%(user)s:%(pw)s@%(host)s:%(port)s/%(db)s' % POSTGRES
db = SQLAlchemy(app)



#need to put some conditions on creating and populating the database and tables
import models
#db.create_all()


import populateDB
#populateDB.initialise_database()


@app.route('/')
def index():
    return render_template('home.html')

@app.route('/getprediction/<date>/<shiftTime>/<crimeType>')
def get_prediction(date, shiftTime, crimeType):

    #create a dataframe from the user data
    user_data = pd.DataFrame(data={'date': [date], 'time': [shiftTime], 'crime_type': [crimeType]})
    print(date)
    user_data['date'] = pd.to_datetime(user_data['date'], format='%d-%m-%Y')
    user_data['year_month'] = user_data['date'].map(lambda x: 100 * x.year + x.month)
    user_data['crime_type'] = user_data['crime_type'].astype(int)
    shift_to_time = {'00:00 - 08:00': 0, '08:00 - 16:00': 1, '16:00 - 00:00': 2}
    user_data['time'] = user_data['time'].map(shift_to_time)

    # check if it contains today's date if not then call api and populate db
    weather_data = pd.read_sql_table("weather", con=app.config['SQLALCHEMY_DATABASE_URI'])
    weather_data['date'] = pd.to_datetime(weather_data['date'], format='%Y-%m-%d')

    # take the weather data for the current day
    user_data = user_data.reset_index(drop=True)
    weather_data = weather_data.reset_index(drop=True)
    scaler = preprocessing.MinMaxScaler()

    scaled_data = scaler.fit_transform(weather_data.loc[:, ['tmax', 'tmin']])
    scaled_data = pd.DataFrame(scaled_data, columns=['tmax', 'tmin'])
    weather_data.loc[:, ['tmax', 'tmin']] = scaled_data.loc[:, ['tmax', 'tmin']]

    weather_data = weather_data[weather_data['date'] == user_data.loc[0,'date']]

    if weather_data.empty:
        # Lookup via latitude and longitude
        w = Weather(Unit.FAHRENHEIT)
        lookup = w.lookup_by_latlng(34.0207305, -118.6919304)

        forecasts = lookup.forecast
        for forecast in forecasts:
            date = models.Weather(datetime.datetime.strptime(forecast.date,'%d %b %Y').strftime('%Y-%m-%d'), float(forecast.high), float(forecast.low))
            db.session.add(date)
            db.session.commit()

        weather_data = pd.read_sql_table("weather", con=app.config['SQLALCHEMY_DATABASE_URI'])
        weather_data['date'] = pd.to_datetime(weather_data['date'], format='%Y-%m-%d')

        scaled_data = scaler.fit_transform(weather_data.loc[:, ['tmax', 'tmin']])
        scaled_data = pd.DataFrame(scaled_data, columns=['tmax', 'tmin'])
        weather_data.loc[:, ['tmax', 'tmin']] = scaled_data.loc[:, ['tmax', 'tmin']]

        #weather_data = weather_data.reset_index(drop=True)
        weather_data = weather_data[weather_data['date'] == user_data.loc[0,'date']]

    #getting the crime data to get the crime statistics
    crime_data = pd.read_sql_table("crime_data", con=app.config['SQLALCHEMY_DATABASE_URI'])

    #getting the zipcode data for the census data etc
    zipcode_data = pd.read_sql_table("zipcode", con=app.config['SQLALCHEMY_DATABASE_URI'])

    #merging all the data together for the prediction
    data = pd.merge(user_data, crime_data,  on=['year_month', 'time', 'crime_type'])
    data = pd.merge(data, zipcode_data, on=['zipcode'])
    data = pd.merge(data, weather_data, on=['date'])
    data = data.drop_duplicates()
    
    print(data.head())
    print(data.info())
    #creating the dummy features for weekday and month
    data.loc[:, 'weekday'] = data.loc[:, 'date'].dt.weekday_name
    data.loc[:,'month'] = data.loc[:,'date'].dt.month
    data['month'] = data['month'].apply(lambda x: calendar.month_abbr[x])

    data = pd.concat([data, pd.get_dummies(data['weekday'])], axis=1)
    data = pd.concat([data, pd.get_dummies(data['month'])], axis=1)

    weekdays = pd.DataFrame({'weekday': ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']})
    data = pd.merge(pd.get_dummies(weekdays.weekday), data, on = data['weekday'].unique().tolist()).fillna(0)

    months = pd.DataFrame({'month': ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']})
    data = pd.merge(pd.get_dummies(months.month), data, on = data['month'].unique().tolist()).fillna(0)

    #changing column data types to int
    data[['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday',
          'Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']] = data[['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday',
                  'Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']].astype(int)


    #need to have the same order of columns as in the model
    columns_order = ['zipcode', 'date', 'geometry', 'weekday', 'month', 'year_month', 'crime_type', 'time', 'count_1m_loc', 'count_6m_loc', 'count_2y_loc', 'count_1m_loc_time', 'count_6m_loc_time', 'count_2y_loc_time', 'count_1m_time', 'count_6m_time', 'count_2y_time', 'Friday', 'Monday', 'Saturday', 'Sunday', 'Thursday', 'Tuesday', 'Wednesday', 'Apr', 'Aug', 'Dec', 'Feb', 'Jan', 'Jul', 'Jun', 'Mar', 'May', 'Nov', 'Oct', 'Sep', 'population', 'density', 'land_area', 'wealthy', 'dist_to_centre', 'dist_to_south', 'total_wages', 'house_of_units', 'crimes_per_pop', 'tmax', 'tmin']
    data = data[columns_order]

    #pkl_file = None
    if(user_data['crime_type'][0] == 1):
        pkl_file = open('ML_models/logmodel_vc.pkl', 'rb')
    else:
        pkl_file = open('ML_models/logmodel_pc.pkl', 'rb')
    model = pickle.load(pkl_file)
    prediction = model.predict(
        data.drop(['zipcode', 'date', 'geometry', 'weekday', 'month', 'year_month', 'crime_type'], axis=1))

    pred = pd.concat((data['zipcode'], data['geometry'], pd.Series(prediction)), axis=1).reset_index().drop('index', axis = 1)

    return pred.to_json(orient='records')



#need to change this to call some method to store the data
@app.route('/upload', methods=['POST'])
def upload():
    if request.method == 'POST':
        print("YASSSSSSS")
        f = request.files['file']
        if f:
            #filename = os.path.join(app.config['UPLOAD_FOLDER'], "%s.%s" % (now.strftime("%Y-%m-%d-%H-%M-%S-%f"), file.filename.rsplit('.', 1)[1]))
            #file.save(filename)
            tempfile_path = tempfile.NamedTemporaryFile().name
            f.save(tempfile_path)
            data = pd.read_csv(tempfile_path, parse_dates=[1])
            populateDB.add_crime_data_to_DB(data)
            return jsonify({"success":True})



if __name__ == "__main__":
    app.run()