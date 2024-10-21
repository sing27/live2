from google.cloud import texttospeech
from google.oauth2 import service_account
import google.generativeai as genai
import os
import time
import dotenv

import base64

dotenv.load_dotenv()

genai.configure(api_key=os.environ['GOOGLE_API_KEY'])


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
    
    def image(self, newfile_path, text_message):
        sample_file = genai.upload_file(path=newfile_path,
                            display_name="Vision_Question")
        
        print("Uploaded file... Text : " + text_message)
        file = genai.get_file(name=sample_file.name)
        print(f"Retrieved file '{file.display_name}' as: {sample_file.uri}")

        while sample_file.state.name == "PROCESSING":
            print('.', end='')
            time.sleep(5)
            sample_file = genai.get_file(sample_file.name)

        if sample_file.state.name == "FAILED":
            raise ValueError(sample_file.state.name)
        
        response = self.model.generate_content([sample_file, text_message])

        imagemessage = response.text

        print(response.text)
        
        return imagemessage



if __name__ == "__main__":
    credentials = service_account.Credentials.from_service_account_file(
        './Key.json')
    googleTTS = GoogleTTS(credentials)
    resault = googleTTS.speak('Hello')
    print(resault)
