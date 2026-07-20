from mlx_lm import load, generate
import queue


class Inference:
    def __init__(self, max_tokens, model_repo='mlx-community/Qwen3-4B-Instruct-2507-4bit'):
        self.model, self.tokenizer = load(model_repo)
        self.max_tokens = max_tokens
        self.response_queue = queue.Queue()

    def generate(self, prompt):
        messages = [{'role': 'user', 'content': prompt}]
        formatted_prompt = self.tokenizer.apply_chat_template(
            messages, add_generation_prompt=True
        )
        response = generate(self.model, self.tokenizer, prompt=formatted_prompt, max_tokens=self.max_tokens)
        self.response_queue.put(response)
        return response

