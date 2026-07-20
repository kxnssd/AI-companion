import threading

from speech.stt.speech_recognition import STT
from llm.inference import Inference

from speech.tts.synthesizer import Synthesizer


class Companion:
    def __init__(self, max_tokens, language: str = 'uk'):
        self.stt = STT(language)
        self.llm = Inference(max_tokens)
        self.running = False

    def _llm_loop(self):
        while self.running:
            user_text = self.stt.text_queue.get()  # blocks until STT produces something
            print(f'$USER:\n{user_text}')
            response = self.llm.generate(user_text)
            print(f'$LLM:\n{response}\n')

    def _synth_loop(self):
        while self.running:
            response = self.llm.response_queue.get()

            synt = Synthesizer()
            synt.synthesize(response)

    def start(self):
        self.running = True
        self.stt.listen()
        threading.Thread(target=self._llm_loop, daemon=True).start()
        threading.Thread(target=self._synth_loop, daemon=True).start()

    def stop(self):
        self.running = False
        self.stt.terminate()

