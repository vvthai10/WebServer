import os
import json
import requests
from flask import Flask, request, render_template, flash
from flask_cors import CORS
from apscheduler.schedulers.background import BackgroundScheduler
requests.packages.urllib3.disable_warnings()

from api.api import api
from models import get_label
from api.ggcloud import transcribe_chirpRecognizer_LongAudio

conn = None
cur = None
PROJECT_ID = "cloudgo-project"
CURRENT_PATH = os.path.dirname(os.path.abspath(__file__))
ROOT_URL = "http://localhost/source/"
ACCESS_TOKEN = ""

def update_label(pbx_manager_id, srcipt, label):
    global ACCESS_TOKEN
    url = ROOT_URL + 'api/OpenAPI/update?module=PBXManager&record=' + pbx_manager_id
    headers = {
        "Access-Token": ACCESS_TOKEN
    }
    data = {
        "data": {
            "script": srcipt,
            "finallabel": label
        }
    }
    print(pbx_manager_id)
    print(data)
    response = requests.post(url, headers=headers, json=data) 
def get_access_token():
    url = ROOT_URL + 'api/OpenAPI/auth?username=admin&access_key_md5=37488f318b75565be18d3b5accb8d439'
    response = requests.get(url)
    data = response.json()
    return data['access_token']
def get_json_data_with_access_token():
    global ACCESS_TOKEN
    url = ROOT_URL + "api/OpenAPI/list?module=PBXManager"
    ACCESS_TOKEN = get_access_token()
    headers = {
        "Access-Token": ACCESS_TOKEN
    }

    response = requests.get(url, headers=headers)
    data = response.json()
    return data
def processing_data(data):
        data = data['entry_list']

        for item in data:
            pbx_manager_id = item["pbxmanagerid"]
            url = item["recordingurl"]
            # finallabel = item["finallabel"]
            finallabel = ""

            if finallabel == "":
                url = url.replace("https://storage.googleapis.com/", "gs://")
                script = transcribe_chirpRecognizer_LongAudio(project_id=PROJECT_ID, gcs_uri=url)
                print(url)
                label = get_label(script)
                print(label)
                update_label(pbx_manager_id, script, label)
def call_api_and_process_data():
    
    DEMO = True
    if DEMO:
        path = os.path.join(CURRENT_PATH, "demo_script.txt")
        with open(path, 'r') as file:
            data = json.load(file)
    else:
        data = get_json_data_with_access_token()

    if data is not None:
        processing_data(data)

def createApp():
    app = Flask(__name__)
    CORS(app)
    app.config['SECRET_KEY']="070602"

    scheduler = BackgroundScheduler()
    scheduler.add_job(call_api_and_process_data, 'interval', seconds=30)
    scheduler.start()

    app.register_blueprint(api, url_prefix='/')
    return app