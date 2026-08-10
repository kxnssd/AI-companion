import json
import re
import queue
import threading

from mlx_lm import load, stream_generate

from tools.registry import TOOLS, call_tool


_TOOL_CALL_RE = re.compile(r"<tool_call>(.*?)</tool_call>", re.DOTALL)

_SYSTEM_PROMPT = (
    "You are a concise voice assistant speaking Ukrainian. "
    "Use the available tools whenever they let you answer "
    "more accurately. After a tool result comes back, give "
    "a short, natural spoken answer, never mention the tool "
    "call itself."
)


class Inference:
    def __init__(
        self,
        max_tokens: int,
        model_repo: str = "mlx-community/Qwen3-4B-Instruct-2507-4bit",
        system_prompt: str = _SYSTEM_PROMPT,
        max_tool_iters: int = 5,
    ):
        self._model, self._tokenizer = load(model_repo)
        self._max_tokens = max_tokens
        self._stop_event = threading.Event()
        self._generator = None
        self._max_tool_iters = max_tool_iters

        self.response_queue = queue.Queue()
        self._messages = [{"role": "system", "content": system_prompt}]

    def generate(self, prompt: str):
        self._stop_event.clear()
        self._messages.append({"role": "user", "content": prompt})

        self._generator = threading.Thread(target=self._run, daemon=True).start()
        return self._generator

    def interrupt(self):
        self._stop_event.set()
        if self._generator and self._generator.is_alive():
            self._generator.join()

    def _run(self):
        for _ in range(self._max_tool_iters):
            if self._stop_event.is_set():
                break

            full_text = self._generate_once()
            if self._stop_event.is_set():
                break

            tool_calls = self._extract_tool_calls(full_text)
            if not tool_calls:
                break

            self._messages.append({"role": "assistant", "content": full_text})
            for call in tool_calls:
                name = call.get("name", "")
                arguments = call.get("arguments", {})
                result = call_tool(name, arguments)

                print(f"$TOOL[{name}]({arguments}) -> {result}", flush=True)

                self._messages.append({
                    "role": "tool",
                    "name": name,
                    "content": str(result),
                })

        self.response_queue.put(None)

    def _generate_once(self) -> str:
        formatted_prompt = self._tokenizer.apply_chat_template(
            self._messages, tools=TOOLS, add_generation_prompt=True
        )

        full_text = ""
        in_tool_call = False

        for response in stream_generate(
            self._model,
            self._tokenizer,
            prompt=formatted_prompt,
            max_tokens=self._max_tokens,
        ):
            if self._stop_event.is_set():
                break

            token = response.text
            full_text += token

            if "<tool_call>" in full_text:
                in_tool_call = True
            if not in_tool_call:
                self.response_queue.put(token)
            if "</tool_call>" in full_text:
                in_tool_call = False

        return full_text

    def _extract_tool_calls(self, text: str) -> list[dict]:
        calls = []
        for block in _TOOL_CALL_RE.findall(text):
            try:
                calls.append(json.loads(block.strip()))
            except json.JSONDecodeError:
                continue
        return calls
