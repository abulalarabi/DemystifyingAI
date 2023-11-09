import os
from flask import send_file, Flask, flash, request, redirect, render_template,url_for, jsonify
from werkzeug.utils import secure_filename
import pandas as pd
from flask_cors import CORS
import time
import shutil
import json
import models

app=Flask(__name__)
#app.secret_key = "secret key"
CORS(app)

filename = "dataset.csv"
supprted_type = ['csv']

def getColumnNames():
    df = pd.read_csv('./dataset/'+filename)
    return list(df.columns)

# route to fetch and download the dataset submitted by a form over POST
@app.route('/dataset', methods=['GET', 'POST'])
def dataset():
    if request.method == 'POST':
        # check if the post request has the file part
        if 'file' not in request.files:
            print("No file part")
            resp = jsonify({'message': 'No file part'})
            resp.headers.add('Access-Control-Allow-Origin', '*')
            return resp,400, {'ContentType':'application/json'}
        
        file = request.files['file']
        # if user does not select file, browser also
        # submit an empty part without filename

        if file.filename == '':
            resp = jsonify({'message': 'No file selected'})
            resp.headers.add('Access-Control-Allow-Origin', '*')
            return resp,400, {'ContentType':'application/json'}
        
        # if the file is valid
        if file:
            # if the dataset.csv exists under /dataset, delete it
            if os.path.exists('/dataset/dataset.csv'):
                os.remove('/dataset/dataset.csv')

            # check if the file is a csv file
            if file.filename.split('.')[-1] in supprted_type:
                # filename = secure_filename(file.filename)
                file.save('./dataset/'+filename)
                print("File uploaded successfully")

                # return the column names of the dataset

                resp = jsonify({'message': 'File uploaded successfully', 'success': True, 'columns': getColumnNames()})
                resp.headers.add('Access-Control-Allow-Origin', '*')
                return resp,200, {'ContentType':'application/json'} 
            else:
                print("File not supported")
                resp = jsonify({'message': 'File not supported'})
                resp.headers.add('Access-Control-Allow-Origin', '*')
                return resp,400, {'ContentType':'application/json'}
    
    # return none if the request is invalid
    resp = jsonify({'message': 'No file selected'})
    resp.headers.add('Access-Control-Allow-Origin', '*')
    return resp,400, {'ContentType':'application/json'}

# route to get decision bounadry plot
@app.route('/decisionboundary', methods=['GET', 'POST'])
def decisionboundary():
    # get json data 
    data = request.get_json()
    if not data:
        resp = jsonify({'message': 'No data found'})
        resp.headers.add('Access-Control-Allow-Origin', '*')
        return resp,400, {'ContentType':'application/json'}
    #data = json.loads(data)

    print(data)

    # get the first and second feature
    feature1 = data['feature1']
    feature2 = data['feature2']

    # get the target
    label = data['target']

    # get the model
    model = data['model']

    # get max depth
    max_depth = int(data['max_depth'])
    
    # create a X and y dataframe
    df = pd.read_csv('./dataset/'+filename)
    X = df[[feature1, feature2]].to_numpy()
    y = df[label].to_numpy()

    if model == 'decision-tree':
        # get the decision boundary plot
        all_frames = models.dtree_figure(X, y, max_depth, feature1, feature2, label)

    # return the plot
    resp = jsonify({'frames': all_frames, 'message': 'Running Model', 'success': True})
    resp.headers.add('Access-Control-Allow-Origin', '*')
    return resp,200, {'ContentType':'application/json'}


# route to run model
@app.route('/runmodel', methods=['GET', 'POST'])
def runmodel():
    # get json data
    data = request.get_json()

    if not data:
        resp = jsonify({'message': 'No data found'})
        resp.headers.add('Access-Control-Allow-Origin', '*')
        return resp,400, {'ContentType':'application/json'}
    
    print(data)

    # get model params
    model = data['model']
    max_depth = int(data['max_depth'])
    leaves = int(data['leaves'])
    label = data['target']

    # create a dataset with all columns except the target
    df = pd.read_csv('./dataset/'+filename)
    X = df.drop(columns=[label]).to_numpy()
    y = df[label].to_numpy()

    # run the model

    if model == 'decision-tree':
        confusion_matrix = models.dtree_model(X, y, max_depth, leaves)
    
    # return the confusion matrix
    resp = jsonify({'confusion_matrix': confusion_matrix, 'message': 'Running Model', 'success': True})
    resp.headers.add('Access-Control-Allow-Origin', '*')
    return resp,200, {'ContentType':'application/json'}


if __name__ == "__main__":
    app.run(host = '0.0.0.0',port = 1407, debug = True)
    #playRecord.play()