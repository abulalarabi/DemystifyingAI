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


# return the list of file
#====================================================================
@app.route('/fetchlist', methods=['GET', 'POST'])
def handle_fetch():
    if request.method == 'POST':
        resp = jsonify({"file_list": 'xyz'})
        resp.headers.add('Access-Control-Allow-Origin', '*')
        return resp,200, {'ContentType':'application/json'}

# receive the button click of the file list
#====================================================================
@app.route('/play', methods=['GET', 'POST'])
def handle_play():
    if request.method == 'POST':
        try:
            indata = request.data.decode("utf-8")
            print('Query: play: ', indata)
            indata = 'record/'+indata+'.json'
            resp = jsonify({"play": 'done'})
            resp.headers.add('Access-Control-Allow-Origin', '*')
            return resp,200, {'ContentType':'application/json'} 
        except:
            resp = jsonify({"error": 'Cannot run'})
            resp.headers.add('Access-Control-Allow-Origin', '*')
            return resp,200, {'ContentType':'application/json'} 

if __name__ == "__main__":
    app.run(host = '0.0.0.0',port = 2307, debug = True)
    #playRecord.play()