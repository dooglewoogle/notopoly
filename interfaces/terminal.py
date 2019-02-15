from common import Game
import logging

class TerminalInterface(object):

    def __init__(self):


        self.logger = logging.Logger("")
        hanlder = logging.StreamHandler()
        self.logger.setLevel(logging.DEBUG)
        self.logger.addHandler(hanlder)

        self.show("Starting...")

        self.game = Game(self.show)


    def show(self, msg):
        self.logger.debug(msg)