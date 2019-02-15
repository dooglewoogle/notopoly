#! /usr/home/dclague/test_virtualenv/bin/python

from common import *

DEFAULT_INTERFACE="terminal"

if __name__ == "__main__":
    if DEFAULT_INTERFACE == "terminal":
        from interfaces import TerminalInterface
        interface = TerminalInterface()
