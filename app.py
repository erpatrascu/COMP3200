# app.py
from flask import Flask, request, render_template
import pickle
#import sklearn
import numpy as np
import pandas as pd

app = Flask(__name__)


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
        try:
            new_vector[index_dict['UNIQUE_CARRIER_' + str(result['unique_carrier'])]] = 1
        except:
            pass
        try:
            new_vector[index_dict['ORIGIN_' + str(result['origin'])]] = 1
        except:
            pass
        try:
            new_vector[index_dict['DEST_' + str(result['dest'])]] = 1
        except:
            pass
        try:
            new_vector[index_dict['DEP_HOUR_' + str(result['dep_hour'])]] = 1
        except:
            pass
        '''

        cols = [0, 1]
        pkl_file = open('models/logmodel.pkl', 'rb')
        logmodel = pickle.load(pkl_file)
        prediction = logmodel.predict(X.drop(X.columns[cols], axis = 1))

        return render_template('result.html', prediction=prediction)

if __name__ == "__main__":
    app.run()