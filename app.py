from flask import Flask, request, render_template, redirect, url_for, jsonify, Response
from flask_cors import CORS
import time
import json
import os
import base64

from python.NewSTT import speech_to_text
from gcp_tts import GoogleTTS
from http import HTTPStatus


from google.oauth2 import service_account


credentials = service_account.Credentials.from_service_account_file(
    './Key.json')
googleTTS = GoogleTTS(credentials)

app = Flask(__name__)
CORS(app)

UPLOAD_FOLDER = 'static/temporary'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)


@app.route('/')
def index():
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

    text = speech_to_text(base64ImageData1)
    response.data = json.dumps({"message": text})
    print(response)

    return response


@app.route('/chat_api', methods=['POST'])
def get_image():
    response = Response(
        content_type="application/json"
    )

    try:

        imageData = request.json.get('imageData')
        requestMessage = request.json.get('message')

        if requestMessage is not None and imageData is None:  # TODO: text only call
            print("*" * 80)
            print(requestMessage)
            text = googleTTS.onlytext(requestMessage)
            response.status_code = 200
            #response.data = json.dumps({"message": text})
            #return response
        elif requestMessage is not None and imageData is not None:
            print("@ " * 60)
            imageFormatData, base64ImageData = imageData.split(',')
            imageFormat = imageFormatData.split('/')[1].split(';')[0]

            # 保存文件
            unique_filename = f"{int(time.time())}_api-image.{imageFormat}"
            file_path = os.path.join(UPLOAD_FOLDER, unique_filename)
            if not os.path.exists(UPLOAD_FOLDER):
                os.makedirs(UPLOAD_FOLDER)
            fh = open(file_path, "wb")
            fh.write(base64.b64decode(base64ImageData))
            fh.close()
            
            print("1")
            text = googleTTS.image(file_path, requestMessage)
            print("2")
            #response.data = json.dumps({"message": text})
        
        print("3:" + text)
        audio = googleTTS.speak(text)
        response.data = json.dumps({"message": text, "ttsAudio": audio})
        print("! " * 60)
        return response

    except Exception as err:
        print("error app")
        print(err)
        response.status = HTTPStatus.INTERNAL_SERVER_ERROR
        response.data = json.dumps({"message": str(err)})
        return response

if __name__ == '__main__':
    app.run(debug=True)
