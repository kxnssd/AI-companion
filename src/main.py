import time
from companion.companion import Companion


def run():
    params = {
        "max_tokens": 20000,
        "stt_language": "uk",
        "synt_language": "uk-UA",
        "min_tokens_to_synth": 8,
    }
    companion = Companion(**params)
    companion.start()

    try:
        while True:
            time.sleep(0.1)
    except KeyboardInterrupt:
        print("Shutting down...")
        companion.stop()


if __name__ == "__main__":
    run()
