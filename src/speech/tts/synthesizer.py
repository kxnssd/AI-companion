import azure.cognitiveservices.speech as speechsdk
from urllib.parse import urlparse

from dotenv import load_dotenv
import os

class Synthesizer:
    def __init__(self):
        load_dotenv()
        self.endpoint_url = os.getenv('AZURE_SPEECH_ENDPOINT')
        self.speech_key = os.getenv('AZURE_SPEECH_KEY')

    def synthesize(self, text, lang="uk-UA"):
        parsed = urlparse(self.endpoint_url)
        base_endpoint = f"{parsed.scheme}://{parsed.netloc}"

        speech_config = speechsdk.SpeechConfig(subscription=self.speech_key, endpoint=base_endpoint)
        speech_config.set_speech_synthesis_output_format(
                    speechsdk.SpeechSynthesisOutputFormat.Riff48Khz16BitMonoPcm
                )
        speech_synthesizer = speechsdk.SpeechSynthesizer(speech_config=speech_config)

        ssml = f"""
        <speak version='1.0' xmlns='http://www.w3.org/2001/10/synthesis' 
               xmlns:mstts='http://www.w3.org/2001/mstts' xml:lang='{lang}'>
            <voice name='en-US-Ava:DragonHDLatestNeural'>
                <lang xml:lang='{lang}'>
                    <prosody pitch='+20%'>
                        {text}
                    </prosody>
                </lang>
            </voice>
        </speak>
        """

        result = speech_synthesizer.speak_ssml_async(ssml).get()

        if result.reason == speechsdk.ResultReason.SynthesizingAudioCompleted:
            print("Speech synthesized for text [{}]".format(text))
        elif result.reason == speechsdk.ResultReason.Canceled:
            cancellation_details = result.cancellation_details
            print("Speech synthesis canceled: {}".format(cancellation_details.reason))
            if cancellation_details.reason == speechsdk.CancellationReason.Error:
                print("Error details: {}".format(cancellation_details.error_details))

