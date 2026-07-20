import time
from companion.companion import Companion


def run():
    companion = Companion(max_tokens=20000)
    companion.start()

    try:
        while True:
            time.sleep(0.1)
    except KeyboardInterrupt:
        print('Shutting down...')
        companion.stop()


if __name__ == '__main__':
    run()
