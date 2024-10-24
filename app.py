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
def get_image():
    response = Response(
        content_type="application/json"
    )

    try:

        imageData = request.json.get('imageData')
        requestMessage = request.json.get('message')

        # hardcode qusestion
        my_dict = CustomDict()
        responsess = my_dict.get_value(requestMessage)

        if responsess == True:
            print(f"Response: {responsess}")
            audio = googleTTS.speak(responsess)
            response.data = json.dumps(
                {"message": responsess, "ttsAudio": audio})
            print("& " * 50)
            return response

        # real chatbot
        if requestMessage is not None and imageData is None:  # TODO: text only call
            print("*" * 80)
            print(requestMessage)
            text = googleTTS.onlytext(requestMessage)
            response.status_code = 200
            # response.data = json.dumps({"message": text})
            # return response
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
            # response.data = json.dumps({"message": text})

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


@app.route('/a', methods=['GET'])
def a():
    jsonFile = open('./a.json', 'r')
    a = json.load(jsonFile)

    message = a.get('message')
    # images_content = a.get('images')
    images_content = []
    chat_id = a.get("chatId") or str(uuid.uuid4())

    chatLLM = ChatLLM(
        credentials=credentials,
        chatId=chat_id
    )
    images = [MessageContentImage.from_uri(img) for img in images_content]
    responses = chatLLM.new_message(message, images)

    print("- " * 50)
    print(responses.content.text)

    return jsonify({'response': responses.content.text})

if __name__ == '__main__':
    app.run(debug=True)
