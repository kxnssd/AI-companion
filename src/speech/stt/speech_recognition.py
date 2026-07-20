import sounddevice as sd
import queue

from moonshine_voice import (
    MicTranscriber,
    TranscriptEventListener,
    get_model_for_language,
)


class TerminalListener(TranscriptEventListener):
    def __init__(self):
        self.last_line_text_length = 0

    def update_last_terminal_line(self, new_text: str):
        print(f"\r{new_text}", end="", flush=True)

        if len(new_text) < self.last_line_text_length:
            diff = self.last_line_text_length - len(new_text)
            print(f"{' ' * diff}", end="", flush=True)

        self.last_line_text_length = len(new_text)

    def on_line_started(self, event):
        self.last_line_text_length = 0

    def on_line_text_changed(self, event):
        self.update_last_terminal_line(event.line.text)

    def on_line_completed(self, event):
        self.update_last_terminal_line(event.line.text)
        print("\n", end="", flush=True)


class QueueListener(TranscriptEventListener):
    def __init__(self, out_queue: queue.Queue):
        self.out_queue = out_queue

    def on_line_completed(self, event):
        text = event.line.text.strip()
        if text:
            self.out_queue.put(text)


class STT:
    def __init__(self, language, model_arch: str | None = None):
        self.model_path, self.model_arch = get_model_for_language(language, model_arch)

        self.mic_index = self._choose_mic()
        self.mic_transcriber = MicTranscriber(
            model_path=self.model_path,
            model_arch=self.model_arch,
            device=self.mic_index,
        )

        self.text_queue = queue.Queue()
        self.mic_transcriber.add_listener(QueueListener(self.text_queue))

        # DEBUG
        # self.mic_transcriber.add_listener(TerminalListener())

    def _choose_mic(self) -> int:
        devices = sd.query_devices()
        for i, info in enumerate(devices):
            if info['max_input_channels'] > 0:
                print(i, info['name'], info['max_input_channels'])
        idx = int(input('Choose your microphone: '))
        return idx

    def listen(self):
        self.mic_transcriber.start()

        print('------------------------ LISTENING ------------------------')

    def terminate(self):
        self.mic_transcriber.stop()
        self.mic_transcriber.close()
