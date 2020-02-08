from li import Li, KEYWORDS
from pyfirmata import Arduino
import time

LINO_KEYWORDS = {
    "lang": {
        **KEYWORDS,
        **{
            'digital_up': 'allumes', 'digital_down': 'eteinds', 'wait': 'attends'
        }
    }
}


class Lino(Li):
    def __init__(self, output='/dev/ttyACM0', lang="lang", keywords=None, ):
        if keywords is None:
            keywords = LINO_KEYWORDS
        super().__init__()
        self.lang = lang
        self.output = output
        self.board = Arduino(self.output)
        self.CATALOG = {
            **self.CATALOG["lang"],
        }

    def digital_write(self, pin, status):
        self.board.digital[pin].write(status)

    def digital_up(self, pin):
        self.digital_write(pin, 1)

    def digital_down(self, pin):
        self.digital_write(pin, 0)

    def wait(self, time_):
        time.sleep(time_)
