# app.py
from flask import Flask, request, render_template
from flask_sqlalchemy import SQLAlchemy
import pickle
import pandas as pd



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
from models import *
#db.create_all()


#import populateDB
#populateDB.initialise_database()


@app.route('/')
def index():
    return render_template('home.html')

@app.route('/getprediction/<date>/<shiftTime>/<crimeType>')
def get_prediction(date, shiftTime, crimeType):
    #try:
       # urlfetch.set_default_fetch_deadline(45)
        #user_data = pd.DataFrame(data={'date': date, 'time': shiftTime, 'crime_type': crimeType})
        user_data = pd.DataFrame(data={'date': [date], 'time': [shiftTime]})
        user_data['date'] = pd.to_datetime(user_data['date'])
        shift_to_time = {'00:00 - 08:00': 0, '08:00 - 16:00': 1, '16:00 - 00:00': 2}
        #user_data['weekday'] = user_data['date'].dt.dayofweek
        #user_data['month'] = user_data['date'].dt.month
        #user_data['year'] = user_data['date'].dt.year
        user_data['time'] = user_data['time'].map(shift_to_time)
        print(user_data)
        print(user_data.info())
        crime_data = pd.read_sql_table("crime_data", con=app.config['SQLALCHEMY_DATABASE_URI'])
        crime_data['date'] = pd.to_datetime(crime_data['date'], format='%Y-%m-%d')
        print(crime_data.info())
        weather_data = pd.read_sql_table("weather", con=app.config['SQLALCHEMY_DATABASE_URI'])
        zipcode_data = pd.read_sql_table("zipcode", con=app.config['SQLALCHEMY_DATABASE_URI'])
        weather_data['date'] = pd.to_datetime(weather_data['date'], format='%Y-%m-%d')
        print(crime_data.info())
        print(weather_data.info())
        print(zipcode_data.info())
        data = pd.merge(user_data, crime_data,  on=['date', 'time'])
        data = pd.merge(data, zipcode_data, on=['zipcode'])

        data = pd.merge(data, weather_data, on=['date'])

        #cols = [0, 1]
        pkl_file = open('ML_models/logmodel.pkl', 'rb')
        logmodel = pickle.load(pkl_file)
        prediction = logmodel.predict(data.drop(['zipcode', 'robbery', 'date'], axis = 1))

        pred = pd.concat((data['zipcode'], pd.Series(prediction)), axis=1).reset_index()
        print(pred)
        #print(prediction)
        return pred.to_json(orient='records')
        #return render_template('result.html', prediction=prediction)
    #except Exception as err:
    #    traceback.print_exc(file=sys.stdout)
    #    return 'Error: ' + repr(err)



if __name__ == "__main__":
    app.run()