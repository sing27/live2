from google.cloud import texttospeech
from google.oauth2 import service_account
import google.generativeai as genai
import os
import time
import dotenv
import requests

import base64

dotenv.load_dotenv()

genai.configure(api_key=os.environ['GOOGLE_API_KEY'])
map_apiKey = os.environ['GOOGLE_MAP_API_KEY']


class GoogleTTS:

    def __init__(self, credentials: service_account.Credentials):

        self.client = texttospeech.TextToSpeechClient(
            credentials=credentials
        )
        self.voice = texttospeech.VoiceSelectionParams(
            language_code="yue-HK",
            name="yue-HK-Standard-A",
        )

        self.audio_config = texttospeech.AudioConfig(
            audio_encoding=texttospeech.AudioEncoding.LINEAR16,
            speaking_rate=1
        )

        self.model = genai.GenerativeModel("gemini-1.5-flash")


    def speak(self, textData: str) -> str:
        input_text = texttospeech.SynthesisInput(text=textData)

        response = self.client.synthesize_speech(
            request={"input": input_text, "voice": self.voice,
                     "audio_config": self.audio_config}
        )

        base64EncodedStr = base64.b64encode(response.audio_content)
        return base64EncodedStr.decode('utf-8')
    
    def onlytext(self, text):
        response = self.model.generate_content(text)
        ans = response.text
        return ans
    
    def geocoding(self, latitude, longitude):
        url = f"https://maps.googleapis.com/maps/api/geocode/json?language=zh-HK&latlng={latitude},{longitude}&key={map_apiKey}"
        print("Url", url)
        response = requests.get(url)
        print(response)
        if response.status_code == 200:
            data = response.json()
            print("Response Data1:", data)
            
            localtion = data['results'][0]['formatted_address']
            print("Response Data2:", localtion)
            
        else:
            print("Error:", response.status_code, response.text)
        return localtion



if __name__ == "__main__":
    credentials = service_account.Credentials.from_service_account_file(
        './Key.json')
    googleTTS = GoogleTTS(credentials)
    resault = googleTTS.speak('Hello')
    print(resault)
