#!/usr/bin/env python

from functools import reduce
import copy
import json
import numbers
import sys
import os
import string


# ##############################################################################
# > Extras functions                                                           #
# ##############################################################################
def _Open(args):
    return os.open(args[0].val.strip(), os.O_RDWR)


def _Read(args):
    return os.read(args[0].val, args[1].val)


def _Write(args):
    return os.write(args[0].val, args[1].val)


def _Close(args):
    return os.close(args[0].val)


CATALOG = {
    'open': _Open,
    'read': _Read,
    'write': _Write,
    'close': _Close
}


# ##############################################################################
# Errors                                                                      #
# ##############################################################################

class Error(Exception):
    pass


class FunctionError(Error):
    def __init__(self, e, name):
        self.name = name.__str__()
        self.e = e

    def __str__(self):
        return self.name + ': ' + self.e.__str__()


class UnboundVariableError(Error):
    def __init__(self, e):
        self.e = e

    def __str__(self):
        return 'unbound variable: ' + self.e.__str__()


class JSOLSyntaxError(Error):
    def __init__(self, msg):
        self.msg = msg

    def __str__(self):
        return self.msg


class ReservedWordError(Error):
    def __init__(self, word):
        self.word = word

    def __str__(self):
        return self.word + ' is a reserved word'

