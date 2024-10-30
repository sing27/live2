from flask import Blueprint, Flask, request, render_template, redirect, url_for, jsonify, Response
from flask_cors import CORS
import time
import uuid
import json
import os
import base64

from python.NewSTT import speech_to_text
from gcp_tts import GoogleTTS
from http import HTTPStatus

from google.oauth2.service_account import Credentials
from json import load
# from hardcodequestion import CustomDict

from chat_llm import ChatLLM, MessageContentImage


credentialsFiles = list(filter(lambda f: f.startswith(
    'gcp_cred') and f.endswith('.json'), os.listdir('.')))
credentials = Credentials.from_service_account_file(
    credentialsFiles[0])
googleTTS = GoogleTTS(credentials)

app = Flask(__name__)
CORS(app)
chatLLM = ChatLLM(credentials=credentials)

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

    Example_Request_Schema = {
        # Context will directly appeded to str and sent to system
        "chatId": "some chat id",
        "context": {
            "location": "lat, lon",
            "language": "en"
        },
        # message and images will be transformed
        "content": {
            "message": "user message",
            "images": ["data url", "data url", "data url"]
        }
    }

    no_data = {"no": "data"}
    request_json: dict = request.json or no_data
    content: dict = request_json.get('content', no_data)
    context: dict = request_json.get('context', no_data)
    message = content.get("message", "")
    images = content.get('images', [])

    # process context
    client_context = ""
    for co in context.keys():
        client_context += f"{co}: {context[co]}"

    # Expected images is a list of string containing src data url for image
    images = list(map(
        lambda img: MessageContentImage.from_uri(img),
        images
    ))

    # return response from llm
    # response.status = HTTPStatus.OK
    # response.response_content = {
    #     "chatId": chatLLM.chatId,
    #     "message": ai_response.content.text,
    # }
    # return response
    # Send to llm
    chatLLM.chatId = request_json.get('chatId', str(uuid.uuid4()))
    ai_response = chatLLM.new_message(
        message=message, images=images, context=client_context)

    # print("3: " + text)
    # audio = googleTTS.speak(text)
    response.data = json.dumps(
        {"message": ai_response.content.text, "ttsAudio": "audio"})
    print("! " * 60)
    return response


@app.route('/api/geocode', methods=['POST'])
def get_geocoding():
    response = Response(
        content_type="application/json"
    )
    lat_lon = request.json.get("location") or ""

    latitude = lat_lon.split(",")[0]
    longitude = lat_lon.split(",")[1]

    geocode_result = googleTTS.geocoding(latitude, longitude)

    response.data = json.dumps({"localtion": geocode_result})

    return response


if __name__ == '__main__':
    # app.run(host="0.0.0.0", port=5000)
    # app.run(host="0.0.0.0", port=5000, ssl_context=('server.crt', 'server.key'))
    print("Starting")
    app.run(debug=True)
