from google.cloud import speech



# STT_CLIENT = speech.SpeechClient.from_service_account_file('gcp_cred-Key.json')

def speech_to_text(credentials, wav): # file_name

    STT_CLIENT = speech.SpeechClient(credentials=credentials)
    # with open(file_name, 'rb') as f:
    #     wav = f.read()
    #     print("$" * 100)
    #     # print(wav)
    #     print("$" * 100)

    audio_file = speech.RecognitionAudio(content=wav)

    config = speech.RecognitionConfig(
        enable_automatic_punctuation = True,
        enable_spoken_emojis = False,
        encoding=speech.RecognitionConfig.AudioEncoding.WEBM_OPUS,
        sample_rate_hertz=48000,
        language_code='yue-Hant-HK',
        alternative_language_codes=['en-US', 'yue-Hant-HK'], #'cmn-Hans-CN'
        use_enhanced = True,
    )

    response = STT_CLIENT.recognize(
        config=config,
        audio=audio_file
    )

    transcript = ''
    for result in response.results:
        transcript += result.alternatives[0].transcript
    print(transcript)
    return transcript
