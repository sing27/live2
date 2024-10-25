from flask import Blueprint, Flask, request, render_template, redirect, url_for, jsonify, Response
from flask_cors import CORS
import time
import json
import os
import base64

from python.NewSTT import speech_to_text
from gcp_tts import GoogleTTS
from mock_chat_llm import *
from http import HTTPStatus

from google.oauth2 import service_account
from json import load
from hardcodequestion import CustomDict


credentialsFiles = list(filter(lambda f: f.startswith(
    'gcp_cred') and f.endswith('.json'), os.listdir('.')))
credentials = Credentials.from_service_account_file(
    credentialsFiles[0])
googleTTS = GoogleTTS(credentials)

app = Flask(__name__)
CORS(app)

UPLOAD_FOLDER = 'static/temporary'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)


@app.route('/')
def index():
    user_agent = request.headers.get('User-Agent')
    if 'Mobile' in user_agent:
        return render_template('m_index.html')
    else:
        return render_template('index.html')


@app.route('/stt', methods=['POST'])
def get_sst():
    response = Response(
        content_type="application/json"
    )

    print("*" * 60)
    imageData = request.json.get('audioData')
    # print(imageData)
    print("!" * 60)
    base64ImageData0 = imageData.split(',')[1]
    base64ImageData1 = base64.b64decode(base64ImageData0)

    text = speech_to_text(credentials, base64ImageData1)
    response.data = json.dumps({"message": text})
    print(response)

    return response


@app.route('/chat_api', methods=['POST'])
def get_information():
    response = Response(
        content_type="application/json"
    )

    try:
        
        imageData = request.json.get('imageData') or []
        requestMessage = request.json.get('message')
        chat_id = request.json.get("chatId") or str(uuid.uuid4())
        latitude = request.json.get("latitude") or ""
        longitude = request.json.get("longitude") or ""
        localtion = request.json.get("localtion") or ""
        
        print(requestMessage,chat_id)
        
        chatLLM = ChatLLM(
            credentials=credentials,
            chatId=chat_id
        )
        
        print("$ " * 80)
        print(requestMessage)
        # imageData = []
        # text = googleTTS.onlytext(requestMessage)
        images = [MessageContentImage.from_uri(img) for img in imageData]
        responses = chatLLM.new_message(requestMessage, images)
        response.status_code = 200
        text = responses.content.text

        print("3:" + text)
        # audio = googleTTS.speak(text)
        response.data = json.dumps({"message": text, "ttsAudio": "audio"})
        print("! " * 60)
        return response

    except Exception as err:
        print("error app")
        print(err)
        response.status = HTTPStatus.INTERNAL_SERVER_ERROR
        response.data = json.dumps({"message": str(err)})
        return response

@app.route('/api/geocode', methods=['POST'])
def get_geocoding():
    response = Response(
        content_type="application/json"
    )
    latitude = request.json.get("latitude") or ""
    longitude = request.json.get("longitude") or ""
    
    geocode_result = googleTTS.geocoding(latitude, longitude)
    
    response.data = json.dumps({"localtion": geocode_result})
    
    return response

if __name__ == '__main__':
    #app.run(host="0.0.0.0", port=5000)
    #app.run(host="0.0.0.0", port=5000, ssl_context=('server.crt', 'server.key'))
    app.run(debug=True)
