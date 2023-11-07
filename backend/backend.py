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
@app.route('/fetch', methods=['GET', 'POST'])
def fetch():
    if request.method == 'POST':
        # check if the post request has the file part
        if 'file' not in request.files:
            print("No file part")
            return redirect(request.url)
        file = request.files['file']
        # if user does not select file, browser also
        # submit an empty part without filename

        if file.filename == '':
            print("No selected file")
            return redirect(request.url)
        
        # if the file is valid
        if file:
            # clear the dataset folder
            shutil.rmtree('dataset')
            os.mkdir('dataset')

            # check if the file is a csv file
            if file.filename.split('.')[-1] in supprted_type:
                # filename = secure_filename(file.filename)
                file.save(os.path.join('dataset', filename))
                
                resp = jsonify({'message': 'File uploaded successfully', 'filename': filename})
                resp.headers.add('Access-Control-Allow-Origin', '*')
                return resp,200, {'ContentType':'application/json'} 
            else:
                resp = jsonify({'message': 'File not supported'})
                resp.headers.add('Access-Control-Allow-Origin', '*')
                return resp,400, {'ContentType':'application/json'}




if __name__ == "__main__":
    app.run(host = '0.0.0.0',port = 2307, debug = True)
    #playRecord.play()