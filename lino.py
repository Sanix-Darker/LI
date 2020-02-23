from li import Li, KEYWORDS
import arduino_firmata.Arduino as Arduino
import arduino_firmata.util as pyfirmata_util
from time import sleep

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
        self.it = pyfirmata_util.Iterator(self.board)
        self.it.start()
        self.CATALOG = {
            **self.CATALOG["lang"],
        }

    def digital_write(self, pin, msg):
        self.board.get_pin('d:' + str(pin) + ':o').write(msg)

    def digital_up(self, pin):
        self.digital_write(pin, 1)

    def digital_down(self, pin):
        self.digital_write(pin, 0)

    def wait(self, time_):
        sleep(time_)
