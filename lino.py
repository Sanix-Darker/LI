from li import Li
from pyfirmata import Arduino
import time

KEYWORDS = {
    "lang": {
        'open': 'open', 'read': 'read', 'write': 'write', 'close': 'close',
        '+': '+', '-': '-', '*': '*', '/': '/', 'print': 'affiche',
        'println': 'affiche_xa', 'scanf': 'demande', '=': '=', '!': '!', '<': '<',
        '>': '>', '<=': '<=', '>=': '>=', 'len': 'taille', 'ins': 'ins', 'del': 'supr',
        'cut': 'cut', 'map': 'map', 'fold': 'fold', 'filter': 'filter', 'assert': 'assert',
        'round': 'round', 'type': 'type', 'import': 'import'
    }
}


class Lino(Li):
    def __init__(self, output='/dev/ttyACM0', lang="lang", keywords=None, ):
        if keywords is None:
            keywords = KEYWORDS
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
