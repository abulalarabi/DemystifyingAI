import os
from flask import send_file, Flask, flash, request, redirect, render_template,url_for, jsonify
from werkzeug.utils import secure_filename
from flask_cors import CORS
import time
import shutil
import json

app=Flask(__name__)
#app.secret_key = "secret key"
CORS(app)

filename = "dataset.csv"
supprted_type = ['csv']

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
                
                resp = jsonify({'message': 'File uploaded successfully', 'success': True})
                resp.headers.add('Access-Control-Allow-Origin', '*')
                return resp,200, {'ContentType':'application/json'} 
            else:
                print("File not supported")
                resp = jsonify({'message': 'File not supported'})
                resp.headers.add('Access-Control-Allow-Origin', '*')
                return resp,400, {'ContentType':'application/json'}
    # return none if the request is invalid
    return None



if __name__ == "__main__":
    app.run(host = '0.0.0.0',port = 1407, debug = True)
    #playRecord.play()