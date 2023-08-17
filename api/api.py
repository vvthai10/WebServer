from flask import Blueprint, request, jsonify
import requests
requests.packages.urllib3.disable_warnings()

import models
import models.voice_command as voicecm
from api.ggcloud import transcribe_chirpRecognizer_LongAudio

api = Blueprint('api', __name__)

@api.route('/transcribe', methods=['POST'])
def transcribe():
    data = request.json
    print("Received data:", data)
    if data['text'].strip() != "":
        message = models.get_command(data['text'])

        response_data = {"status": "success", "message": message}
    else:
        response_data = {"status": "success", "message": "none"}
    return jsonify(response_data), 200
    # transcript = transcribe_chirpRecognizer_LongAudio()
    # return render_template('transcribed.html', transcript=transcript)

@api.route("/testapi", methods=["GET"])
def testAPI():
    response_data = {"status": "success", "message": "This is demo api"}
    return jsonify(response_data), 200

@api.route("/testtranscript", methods=["GET"])
def transcribeVoiceToText():
    project_id = "cloudgo-project"
    gcs_uri = "https://storage.googleapis.com/cloudgo_bucket/audio-files/Record3.wav"
    gcs_uri = gcs_uri.replace("https://storage.googleapis.com/", "gs://")
    transcript = transcribe_chirpRecognizer_LongAudio(project_id, gcs_uri)
    response_data = {"status": "success", "message": transcript}
    return jsonify(response_data), 200

@api.route("/test_get_token", methods=["GET"])
def testGetToken():
    data = request.json
    print("CHECK RIGHT HERE")
    print(data)
    url = data['url']
    print(url)
    response = requests.get(url)
    data = response.json()
    try:
        response = requests.get(url)
        data = response.json()
        response_data = {"status": "success", "message": data['access_token']}
    except:
        response_data = {"status": "Error", "message": "Some error"}
    return jsonify(response_data), 200

@api.route("/train_voice_command", methods=["GET"])
def trainModelVoiceCommand():
    voicecm.train()
    response_data = {"status": "success", "message": "Train successful"}
    return jsonify(response_data), 200
