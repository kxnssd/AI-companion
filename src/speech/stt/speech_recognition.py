import sounddevice as sd
import queue

from moonshine_voice import (
    MicTranscriber,
    TranscriptEventListener,
    get_model_for_language,
)


class QueueListener(TranscriptEventListener):
    def __init__(self, out_queue: queue.Queue):
        self.out_queue = out_queue
        self.currently_speaking = False

    def on_line_text_changed(self, event):
        self.currently_speaking = True

    def on_line_completed(self, event):
        self.currently_speaking = False
        text = event.line.text.strip()
        if text:
            self.out_queue.put(text)


class STT:
    def __init__(self, language: str, model_arch: str | None = None):
        self.model_path, self.model_arch = get_model_for_language(language, model_arch)

        self.mic_index = self._choose_mic()
        self.mic_transcriber = MicTranscriber(
            model_path=self.model_path,
            model_arch=self.model_arch,
            device=self.mic_index,
        )

        self.text_queue = queue.Queue()
        self.listener = QueueListener(self.text_queue)
        self.mic_transcriber.add_listener(self.listener)

    def _choose_mic(self) -> int:
        devices = sd.query_devices()
        for i, info in enumerate(devices):
            if info["max_input_channels"] > 0:
                print(i, info["name"], info["max_input_channels"])
        idx = int(input("Choose your microphone: "))
        return idx

    def listen(self):
        self.mic_transcriber.start()

        print("------------------------ LISTENING ------------------------")

    def is_speaking(self) -> bool:
        return self.listener.currently_speaking

    def terminate(self):
        self.mic_transcriber.stop()
        self.mic_transcriber.close()


