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


@app.route('/getdelay', methods=['POST', 'GET'])
def get_delay():
    if request.method == 'POST':
        result = request.form

        data = pd.read_csv('datasets/example.csv')
        X = data[data['zipcode'] == int(result['zipcode'])]

        '''
        # Prepare the feature vector for prediction
        pkl_file = open('cat', 'rb')
        index_dict = pickle.load(pkl_file)
        new_vector = np.zeros(len(index_dict))

        try:
            new_vector[index_dict['DAY_OF_WEEK_' + str(result['day_of_week'])]] = 1
        except:
            pass

        '''

        cols = [0, 1]
        pkl_file = open('ML_models/logmodel.pkl', 'rb')
        logmodel = pickle.load(pkl_file)
        prediction = logmodel.predict(X.drop(X.columns[cols], axis = 1))

        return render_template('result.html', prediction=prediction)

if __name__ == "__main__":
    app.run()