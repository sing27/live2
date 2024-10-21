from concurrent.futures import thread
import queue
import re
import sys
import time
import threading
#import ollama

from google.cloud import speech
from google.oauth2 import service_account

import pyaudio

# Audio recording parameters
RATE = 16000
CHUNK = int(RATE / 10)  # 100ms


class MicrophoneStream:
    global running
    """Opens a recording stream as a generator yielding the audio chunks."""

    def __init__(self: object, rate: int = RATE, chunk: int = CHUNK) -> None:
        """The audio -- and generator -- is guaranteed to be on the main thread."""
        self._rate = rate
        self._chunk = chunk

        # Create a thread-safe buffer of audio data
        self._buff = queue.Queue()
        self.closed = True

    def __enter__(self: object) -> object:
        self._audio_interface = pyaudio.PyAudio()
        self._audio_stream = self._audio_interface.open(
            format=pyaudio.paInt16,
            # The API currently only supports 1-channel (mono) audio
            # https://goo.gl/z757pE
            channels=1,
            rate=self._rate,
            input=True,
            frames_per_buffer=self._chunk,
            # Run the audio stream asynchronously to fill the buffer object.
            # This is necessary so that the input device's buffer doesn't
            # overflow while the calling thread makes network requests, etc.
            stream_callback=self._fill_buffer,
        )

        self.closed = False
        return self

    def __exit__(
        self: object,
        type: object,
        value: object,
        traceback: object,
    ) -> None:
        """Closes the stream, regardless of whether the connection was lost or not."""
        self._audio_stream.stop_stream()
        self._audio_stream.close()
        self.closed = True
        # Signal the generator to terminate so that the client's
        # streaming_recognize method will not block the process termination.
        self._buff.put(None)
        self._audio_interface.terminate()
        print("_exit")

    def _fill_buffer(
        self: object,
        in_data: object,
        frame_count: int,
        time_info: object,
        status_flags: object,
    ) -> object:
        """Continuously collect data from the audio stream, into the buffer.

        Args:
            in_data: The audio data as a bytes object
            frame_count: The number of frames captured
            time_info: The time information
            status_flags: The status flags

        Returns:
            The audio data as a bytes object
        """
        self._buff.put(in_data)
        #print("4")
        return None, pyaudio.paContinue

    def generator(self: object) -> object:
        """Generates audio chunks from the stream of audio data in chunks.

        Args:
            self: The MicrophoneStream object

        Returns:
            A generator that outputs audio chunks.
        """
        while not self.closed:
            # Use a blocking get() to ensure there's at least one chunk of
            # data, and stop iteration if the chunk is None, indicating the
            # end of the audio stream.
            chunk = self._buff.get()
            if running is False:
                break
            if chunk is None:
                return
            data = [chunk]
            #print("5")

            # Now consume whatever other data's still buffered.
            while True:
                try:
                    chunk = self._buff.get(block=False)
                    if chunk is None:
                        return
                    data.append(chunk)
                    #print("7")
                except queue.Empty:
                    #print("8")
                    break

            yield b"".join(data)
            #print("6")

# threading
X = 7
time_started = time.time()
running = True # 线程的运行状态
pause_event = threading.Event() # 用于控制线程的暂停和继续
final_transcript = ""
time_check = 0

def timer():
    global time_started, running, final_transcript, time_check

    try:
        while running:
            pause_event.wait()
            if time.time() > time_started + X:
                print(final_transcript)
                running = False
                break  # or raise TimeoutException() continue
    except:
        print("timerbreak")
            

        print (time_check) # time +1s
        time.sleep(1)
        time_check += 1




def listen_print_loop(responses: object) -> str:
    
    global final_transcript, time_started, time_check, running
    """Iterates through server responses and prints them.

    The responses passed is a generator that will block until a response
    is provided by the server.

    Each response may contain multiple results, and each result may contain
    multiple alternatives; for details, see https://goo.gl/tjCPAU.  Here we
    print only the transcription for the top alternative of the top result.

    In this case, responses are provided for interim results as well. If the
    response is an interim one, print a line feed at the end of it, to allow
    the next result to overwrite it, until the response is a final one. For the
    final one, print a newline to preserve the finalized transcription.

    Args:
        responses: List of server responses

    Returns:
        The transcribed text.
    """
    num_chars_printed = 0
    time_started = time.time()  # 记录开始时间
    #final_transcript = ""  # Store the final transcript


    #try:
    for response in responses:
        if not response.results:
            continue

        # The `results` list is consecutive. For streaming, we only care about
        # the first result being considered, since once it's `is_final`, it
        # moves on to considering the next utterance.
        result = response.results[0]

        if not result.alternatives:
            continue

        # Display the transcription of the top alternative.
        transcript = result.alternatives[0].transcript

        # Display interim results, but with a carriage return at the end of the
        # line, so subsequent lines will overwrite them.
        #
        # If the previous result was longer than this one, we need to print
        # some extra spaces to overwrite the previous result
        overwrite_chars = " " * (num_chars_printed - len(transcript))

        if not result.is_final:
            sys.stdout.write(transcript + overwrite_chars + "\r")
            sys.stdout.flush()

            num_chars_printed = len(transcript)
            time_started = time.time()
        
        else:
            print(transcript + overwrite_chars)
            final_transcript += transcript + overwrite_chars  # Update final transcript

            # Exit recognition if any of the transcribed phrases could be
            # one of our keywords.
            if re.search(r"\b(再見|大師|master)\b", transcript, re.I):
                print("Good Bye!")
                running = False
                break

        num_chars_printed = 0


#### local chatbot


client_file = 'SLL_demo.json'
credentials = service_account.Credentials.from_service_account_file(client_file)


def steamingspeech() -> None:

    """Transcribe speech from audio file."""
    # See http://g.co/cloud/speech/docs/languages
    # for a list of supported languages.
 #   alternative_language_code = ['ja-JP', 'en-US']  # a BCP-47 language tag 'ja-JP' 'en-US' 'yue-Hant-HK' 'cmn-Hans-CN'

    client = speech.SpeechClient(credentials=credentials)
    config = speech.RecognitionConfig(
        encoding=speech.RecognitionConfig.AudioEncoding.LINEAR16,
        sample_rate_hertz=RATE,
        language_code='yue-Hant-HK',
        alternative_language_codes=['en-US', 'yue-Hant-HK', 'cmn-Hans-CN'],
  #      alternative_language_codes=alternative_language_code,
    )

    streaming_config = speech.StreamingRecognitionConfig(
        config=config, interim_results=True
    )

    with MicrophoneStream(RATE, CHUNK) as stream:
        print("Starting Now")
        t1 = threading.Thread(target=timer)
        t1.start()
        pause_event.set()

        audio_generator = stream.generator()

        requests = (
            speech.StreamingRecognizeRequest(audio_content=content)
                for content in audio_generator
        )

        responses = client.streaming_recognize(streaming_config, requests)
        #print(vars(responses))

        # Now, put the transcription responses to use.
        #listen_print_loop([res])
        listen_print_loop(responses)






def get_text():
    global time_started ,final_transcript, running
    running = True
    final_transcript = ""
    time_started = time.time()
    steamingspeech()
    print("test : " + final_transcript)
    return final_transcript

if __name__ == "__main__":
    get_text()