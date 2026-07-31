import queue
import threading
from mlx_lm import load, stream_generate


class Inference:
    def __init__(
        self,
        max_tokens: int,
        model_repo: str = "mlx-community/Qwen3-4B-Instruct-2507-4bit",
    ):
        self._model, self._tokenizer = load(model_repo)
        self._max_tokens = max_tokens
        self._stop_event = threading.Event()
        self._generator = None

        self.response_queue = queue.Queue()

    def generate(self, prompt: str):
        self._stop_event.clear()
        self._generator = threading.Thread(
            target=self._run, args=(prompt,), daemon=True
        ).start()
        return self._generator

    def interrupt(self):
        self._stop_event.set()
        if self._generator and self._generator.is_alive():
            self._generator.join()

    def _run(self, prompt: str):
        messages = [{"role": "user", "content": prompt}]

        formatted_prompt = self._tokenizer.apply_chat_template(
            messages, add_generation_prompt=True
        )

        for response in stream_generate(
            self._model,
            self._tokenizer,
            prompt=formatted_prompt,
            max_tokens=self._max_tokens,
        ):
            if self._stop_event.is_set():
                break
            self.response_queue.put(response.text)
        self.response_queue.put(None)
