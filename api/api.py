from flask import Blueprint, request, jsonify
import requests
requests.packages.urllib3.disable_warnings()

import models
import models.voice_command as voicecm

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
def transcribeVoiceToText():
    response_data = {"status": "success", "message": "This is demo api"}
    return jsonify(response_data), 200

@api.route("/train_voice_command", methods=["GET"])
def trainModelVoiceCommand():
    voicecm.train()
    response_data = {"status": "success", "message": "Train successful"}
    return jsonify(response_data), 200
