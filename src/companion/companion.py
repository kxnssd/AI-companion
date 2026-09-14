import threading
import queue
import time

from speech.stt.speech_recognition import STT
from llm.inference import Inference

from speech.tts.synthesizer import Synthesizer


class Companion:
    def __init__(
        self,
        max_tokens: int,
        stt_language: str = "uk",
        synt_language: str = "uk-UA",
        min_tokens_to_synth: int = 100,
    ):
        self.stt = STT(stt_language)
#, model_repo="mlx-community/Qwen3-14B-4bit"
        self.llm = Inference(max_tokens)
        self.synt = Synthesizer(synt_language, min_tokens_to_synth)

        self.tts_queue = queue.Queue()
        self.running = False

    def _interrupt_speech(self):
        self.synt.stop()

        while not self.tts_queue.empty():
            try:
                self.tts_queue.get_nowait()
            except queue.Empty:
                break

    def _monitor_user_speech_loop(self):
        while self.running:
            self._interrupt_on_speaking()
            time.sleep(0.1)

    def _llm_loop(self):
        while self.running:
            user_text = self.stt.text_queue.get()
            print(f"\n$USER:\n{user_text}", flush=True)

            self.llm.generate(user_text)
            print(f"$LLM:\n", flush=True)

            sent_buffer = ""
            token_count = 0

            while True:
                token = self.llm.response_queue.get()

                if token is None:
                    if sent_buffer:
                        self.tts_queue.put(sent_buffer)
                    break

                print(token, end="", flush=True)

                sent_buffer += token
                token_count += 1

                if (
                    any(punct in token for punct in [".", "!", "?", "\n"])
                    and token_count >= self.synt.min_tokens_to_synth
                ):
                    self.tts_queue.put(sent_buffer)
                    sent_buffer = ""
                    token_count = 0

    def _interrupt_on_speaking(self):
        if self.stt.is_speaking():
            self._interrupt_speech()
            self.llm.interrupt()

    def _synth_loop(self):
        while self.running:
            response = self.tts_queue.get()
            if response:
                self.synt.synthesize(response)

    def start(self):
        self.running = True
        self.stt.listen()
        threading.Thread(target=self._llm_loop, daemon=True).start()
        threading.Thread(target=self._synth_loop, daemon=True).start()
        threading.Thread(target=self._monitor_user_speech_loop, daemon=True).start()

    def stop(self):
        self.running = False
        self._interrupt_speech()
        self.stt.terminate()
