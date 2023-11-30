import os
from flask import send_file, Flask, flash, request, redirect, render_template,url_for, jsonify
from werkzeug.utils import secure_filename
import pandas as pd
from flask_cors import CORS
import models
from sklearn.preprocessing import LabelEncoder
from sklearn.model_selection import train_test_split
import json

app=Flask(__name__)
#app.secret_key = "secret key"
CORS(app)

filename = "dataset.csv"
supprted_type = ['csv']
model = None
model_type = None
df = None
label = None
model_type = None
filtered_columns = None

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

    all_frames = models.decision_figure(X, y, max_depth, feature1, feature2, label, model)

    # return the plot
    resp = jsonify({'frames': all_frames, 'message': 'Running Model', 'success': True})
    resp.headers.add('Access-Control-Allow-Origin', '*')
    return resp,200, {'ContentType':'application/json'}


# route to run model
@app.route('/runmodel', methods=['GET', 'POST'])
def runmodel():
    global model, model_type, df, label, filtered_columns
    # get json data
    data = request.get_json()

    if not data:
        resp = jsonify({'message': 'No data found'})
        resp.headers.add('Access-Control-Allow-Origin', '*')
        return resp,400, {'ContentType':'application/json'}
    
    print(data)

    # get model params
    model_name = data['model']
    model_type = data['model_type']
    max_depth = int(data['max_depth'])
    leaves = int(data['leaves'])
    label = data['target']
    split = float(data['split'])

    # create a dataset with all columns except the target
    df = pd.read_csv('./dataset/'+filename)

    # get filtered columns
    filtered_columns = data['filter_columns']

    # if the filter columns is not empty, drop the columns
    if filtered_columns:
        df = df.drop(columns=filtered_columns)
    
    
    # check each column and encode it if it is not numeric
    for column in df.columns:
        if df[column].dtype == 'object' and column != label:
            le = LabelEncoder()
            df[column] = le.fit_transform(df[column])

    # split the dataset into train and test
    df_train, df_test = train_test_split(df, test_size=split, random_state=42)

    X = df_train.drop(columns=[label])
    y = df_train[label]
    
    # run the model
    if model_name == 'decision-tree':
        model = models.dtree_model(X, y, max_depth, leaves, model_type)
    elif model_name == 'random-forest':
        model = models.random_forest_model(X, y, max_depth, leaves, model_type)
    
    confusion_matrix = models.getConfusion(model, df_test.drop(columns=[label]), df_test[label], model_type)
    
    metrics = models.getMetrics(df_test[label], model.predict(df_test.drop(columns=[label])), model_type)

    shap_values = models.getShapFigure(model,X,y,model_type)


    # return the confusion matrix
    resp = jsonify({'metrics':metrics,'confusion_matrix': confusion_matrix, 'message': 'Running Model', 'success': True, 'shap_values': shap_values})
    resp.headers.add('Access-Control-Allow-Origin', '*')
    return resp,200, {'ContentType':'application/json'}

# route to get individual shap values
@app.route('/individualshap', methods=['GET', 'POST'])
def individualshap():
    # get json data
    data = request.get_json()

    if not data:
        resp = jsonify({'message': 'No data found'})
        resp.headers.add('Access-Control-Allow-Origin', '*')
        return resp,400, {'ContentType':'application/json'}
    
    print(data)

    # get the feature
    feature = data['feature']

    # get the shap values
    shap_values = models.getIndividualShap(model, df.drop(columns=[label]), df[label], feature, model_type)

    # return the shap values
    resp = jsonify({'shap_values': shap_values, 'message': 'Obtaining Data', 'success': True})
    resp.headers.add('Access-Control-Allow-Origin', '*')
    return resp,200, {'ContentType':'application/json'}

# route to get individual shap values
@app.route('/interaction', methods=['GET', 'POST'])
def interaction():
    # get json data
    data = request.get_json()

    if not data:
        resp = jsonify({'message': 'No data found'})
        resp.headers.add('Access-Control-Allow-Origin', '*')
        return resp,400, {'ContentType':'application/json'}
    
    print(data)

    # get the feature
    feature1 = data['feature1']
    feature2 = data['feature2']

    # get the shap values
    feature_interaction = models.getInteraction(model, df.drop(columns=[label]), df[label], feature1, feature2, model_type)

    # return the shap values
    resp = jsonify({'feature_interaction': feature_interaction, 'message': 'Obtaining Data', 'success': True})
    resp.headers.add('Access-Control-Allow-Origin', '*')
    return resp,200, {'ContentType':'application/json'}

# route to get individual shap values
@app.route('/partial', methods=['GET', 'POST'])
def partial():
    # get json data
    data = request.get_json()

    if not data:
        resp = jsonify({'message': 'No data found'})
        resp.headers.add('Access-Control-Allow-Origin', '*')
        return resp,400, {'ContentType':'application/json'}
    
    print(data)

    # get the feature
    feature = data['feature']

    # get the shap values
    partial_data = models.getPartial(model, df.drop(columns=[label]), df[label], feature, model_type)

    # return the shap values
    resp = jsonify({'partial_data': partial_data, 'message': 'Obtaining Data', 'success': True})
    resp.headers.add('Access-Control-Allow-Origin', '*')
    return resp,200, {'ContentType':'application/json'}


# route to get individual shap values
@app.route('/interactionsummary', methods=['GET', 'POST'])
def interactionsummary():
    # get json data
    data = request.get_json()

    if not data:
        resp = jsonify({'message': 'No data found'})
        resp.headers.add('Access-Control-Allow-Origin', '*')
        return resp,400, {'ContentType':'application/json'}
    
    print(data)

    # get the feature
    feature = data['feature']

    # get the shap values
    interaction_summary = models.getInteractionSummary(model, df.drop(columns=[label]), df[label], feature, model_type)

    # return the shap values
    resp = jsonify({'interaction_summary': interaction_summary, 'message': 'Obtaining Data', 'success': True})
    resp.headers.add('Access-Control-Allow-Origin', '*')
    return resp,200, {'ContentType':'application/json'}


# route to get pr curve
@app.route('/getpr', methods=['GET', 'POST'])
def getpr():
    # get json data
    data = request.get_json()

    if not data:
        resp = jsonify({'message': 'No data found'})
        resp.headers.add('Access-Control-Allow-Origin', '*')
        return resp,400, {'ContentType':'application/json'}
    
    print(data)

    # get the feature
    cut_off = data['cut_off']

    # get the shap values
    pr = models.getPr(model, df.drop(columns=[label]), df[label], cut_off, model_type)

    # return the shap values
    resp = jsonify({'pr': pr, 'message': 'Obtaining Data', 'success': True})
    resp.headers.add('Access-Control-Allow-Origin', '*')
    return resp,200, {'ContentType':'application/json'}

# route to get roc curve
@app.route('/getroc', methods=['GET', 'POST'])
def getroc():
    # get json data
    data = request.get_json()

    if not data:
        resp = jsonify({'message': 'No data found'})
        resp.headers.add('Access-Control-Allow-Origin', '*')
        return resp,400, {'ContentType':'application/json'}
    
    print(data)

    # get the feature
    cut_off = data['cut_off']
    feature = data['feature']

    # get the shap values
    roc = models.getRoc(model, df.drop(columns=[label]), df[label], cut_off, model_type, feature)

    # return the shap values
    resp = jsonify({'roc': roc, 'message': 'Obtaining Data', 'success': True})
    resp.headers.add('Access-Control-Allow-Origin', '*')
    return resp,200, {'ContentType':'application/json'}

# route to get contribution plot
@app.route('/contribution', methods=['GET', 'POST'])
def contribution():
    # get json data
    data = request.get_json()

    if not data:
        resp = jsonify({'message': 'No data found'})
        resp.headers.add('Access-Control-Allow-Origin', '*')
        return resp,400, {'ContentType':'application/json'}
    
    print(data)

    # get the feature
    indx = data['index']

    # get the shap values
    interaction_summary = models.getContribution(model, df.drop(columns=[label]), df[label], indx, model_type)

    # return the shap values
    resp = jsonify({'interaction_summary': interaction_summary, 'message': 'Obtaining Data', 'success': True})
    resp.headers.add('Access-Control-Allow-Origin', '*')
    return resp,200, {'ContentType':'application/json'}

if __name__ == "__main__":
    app.run(host = '0.0.0.0',port = 1407, debug = True)
    #playRecord.play()