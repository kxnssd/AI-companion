import os
from dotenv import load_dotenv

from urllib.parse import urlparse
import azure.cognitiveservices.speech as speechsdk


class Synthesizer:
    def __init__(self, target_lang: str, min_tokens_to_synth: int):
        load_dotenv()
        self.endpoint_url = os.getenv("AZURE_SPEECH_ENDPOINT")
        self.speech_key = os.getenv("AZURE_SPEECH_KEY")
        self.target_lang = target_lang
        self.min_tokens_to_synth = min_tokens_to_synth

        parsed = urlparse(self.endpoint_url)
        base_endpoint = f"{parsed.scheme}://{parsed.netloc}"

        self.speech_config = speechsdk.SpeechConfig(
            subscription=self.speech_key, endpoint=base_endpoint
        )
        self.speech_config.set_speech_synthesis_output_format(
            speechsdk.SpeechSynthesisOutputFormat.Riff48Khz16BitMonoPcm
        )

        self.speech_synthesizer = speechsdk.SpeechSynthesizer(
            speech_config=self.speech_config
        )

    def synthesize(self, text: str):
        if not text or not text.strip():
            return

        ssml = f"""
        <speak version='1.0' xmlns='http://www.w3.org/2001/10/synthesis' 
               xmlns:mstts='http://www.w3.org/2001/mstts' xml:lang='{self.target_lang}'>
            <voice name='en-US-Ava:DragonHDLatestNeural'>
                <lang xml:lang='{self.target_lang}'>
                    <prosody pitch='+20%'>
                        {text}
                    </prosody>
                </lang>
            </voice>
        </speak>
        """

        result = self.speech_synthesizer.speak_ssml(ssml)

        if result.reason == speechsdk.ResultReason.Canceled:
            cancellation_details = result.cancellation_details
            if cancellation_details.reason == speechsdk.CancellationReason.Error:
                print(f"TTS Error: {cancellation_details.error_details}")

    def stop(self):
        if self.speech_synthesizer:
            self.speech_synthesizer.stop_speaking_async()
