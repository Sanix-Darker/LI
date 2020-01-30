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


###############################################################################
# Types                                                                       #
###############################################################################

class Type(object):
    pass


class Literal(Type):
    def __init__(self, val, env):
        self.env = env
        self.val = copy.copy(val)

    def __eq__(self, o):
        return self.val == o.val

    def __str__(self):
        return str(self.val)

    def json(self):
        return dict([('lit', self.val)])


class List(Literal):
    def __init__(self, val, env):
        super(List, self).__init__(val, env)
        for (i, v) in enumerate(self.val):
            self.val[i] = _Eval(v, env)

    def __str__(self):
        return str(map(lambda x: x.__str__(), self.val))

    def json(self):
        return dict([('lit', map(lambda x: x.json(), self.val))])


class Dict(Literal):
    def __init__(self, val, env):
        super(Dict, self).__init__(val, env)
        dict_env = env.copy()
        for (k, v) in self.val.iteritems():
            self.val[k] = _Eval(v, dict_env)
        for v in self.val.values():
            if isinstance(v, Function):
                v._env = self.val

    def json(self):
        return dict([('lit',
                      dict(zip(self.val.keys(),
                               map(lambda x: x.json(), self.val.values()))))])


class String(Literal):
    pass


class Number(Literal):
    def json(self):
        return self.val


class Null(Literal):
    def json(self):
        return self.val

    def __str__(self):
        return 'Null'


class Function(Type):
    class _FunctionEnv(object):
        def __init__(self, env, run_env, og_func):
            self.val = og_func
            self._env = env
            self._run_env = run_env

        def copy(self):
            env = {}
            env.update(self._env)
            env.update(self._run_env)
            return env

        def __eq__(self, o):
            return o == self.val

        def get(self, k, default=None):
            return self.copy().get(k, default)

        def __getitem__(self, k):
            return self.copy()[k]

        def __setitem__(self, k, v):
            if k in self._run_env or k not in self._env:
                self._run_env[k] = v
            else:
                self._env[k] = v

    def __init__(self, d, env):
        self._env = env.copy()
        self._params = d.get('params', [])
        self._def = d.get('def', [])
        self._run_env = {}
        self.val = self

    def json(self):
        return dict([('params', self._params), ('def', self._def)])

    def Eval(self, args):
        return _ExecList(
            self._def,
            self._FunctionEnv(self._env, dict(zip(self._params, args)), self))


def Lit(val, env=None):
    if env is None:
        env = {}
    if isinstance(val, Type):
        return val
    return LITERALS[type(val)](val, env)


TYPES = {
    List: "List",
    Dict: "Dict",
    String: "String",
    Number: "Number",
    Function: "Function",
    Null: "Null"
}

NoneType = type(None)

LITERALS = {
    list: List,
    dict: Dict,
    str: String,
    int: Number,
    bool: Number,
    float: Number,
    NoneType: Null,
}

