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
ROOT_URL = "https://dev.cloudpro.vn/"
USER_NAME = "vy.ngo"
ACCESS_KEY = "db3cda88f740f6b8191c64886ae16ff3"
ACCESS_TOKEN = ""
IS_RUN = False

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
    url = ROOT_URL + f'api/OpenAPI/auth?username={USER_NAME}&access_key_md5={ACCESS_KEY}'
    response = requests.get(url)
    data = response.json()
    # return data['access_token']
    return data['data']['access_token']
def get_json_data_with_access_token(offset):
    global ACCESS_TOKEN
    url = ROOT_URL + f"api/OpenAPI/list?module=PBXManager&sort_column=modifiedtime&sort_order=DESC&offset={offset}&max_rows=50"
    headers = {
        "Access-Token": ACCESS_TOKEN
    }

    response = requests.get(url, headers=headers)
    data = response.json()
    return data
def processing_data(data):
        data = data['data']['entry_list']

        for item in data:
            pbx_manager_id = item["pbxmanagerid"]
            url = item["recordingurl"]
            # finallabel = item["finallabel"]
            finallabel = ""
            if not "https://storage.googleapis.com/" in url:
                print("[WARNING]: ID: " +str(pbx_manager_id) + " have URL of record not true: " + url)
                continue
            if finallabel == "":
                print("[START TRANSCRIPT]: ID: " + str(pbx_manager_id) + " with link: " + url)
                url = url.replace("https://storage.googleapis.com/", "gs://")
                script = transcribe_chirpRecognizer_LongAudio(project_id=PROJECT_ID, gcs_uri=url)
                label = get_label(script)
                print("\tLABEL GET: " + label)
                update_label(pbx_manager_id, script, label)
def call_api_and_process_data():
    global ACCESS_TOKEN
    global IS_RUN
    if not IS_RUN:
        IS_RUN = True
        DEMO = False
        if DEMO:
            path = os.path.join(CURRENT_PATH, "demo_script.txt")
            with open(path, 'r') as file:
                data = json.load(file)
            if data is not None:
                processing_data(data)
        else:
            ACCESS_TOKEN = get_access_token()
            offset = 0
            print("Start with offset: ", offset)
            while offset != -1:
                data = get_json_data_with_access_token(offset)
                paging = data["data"]["paging"]
                print(paging)
                if 'next_offset' in paging.keys():
                    offset = int(paging['next_offset'])
                else:
                    offset = -1
                processing_data(data)
            print("Done")
            
        IS_RUN = False

def createApp():
    app = Flask(__name__)
    CORS(app)
    app.config['SECRET_KEY']="070602"

    scheduler = BackgroundScheduler()
    scheduler.add_job(call_api_and_process_data, 'interval', seconds=900)
    scheduler.start()

    app.register_blueprint(api, url_prefix='/')
    return app