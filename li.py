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


###############################################################################
# Built-in Functions                                                          #
###############################################################################

def _Cond(func, val):
    return all(func(val[i].val, val[i + 1].val) for i in range(len(val) - 1))


def _Add(args):
    return reduce(lambda x, y: Lit(x.val + y.val), args)


def _Sub(args):
    return reduce(lambda x, y: Lit(x.val - y.val), args)


def _Mult(args):
    return reduce(lambda x, y: Lit(x.val * y.val), args)


def _Div(args):
    return reduce(lambda x, y: Lit(x.val / y.val), args)


def _Println(args):
    for arg_ in args:
        print(arg_)
        print()


def _Print(args):
    for arg_ in args:
        sys.stdout.write(arg_.__str__())
    sys.stdout.flush()


def _Eq(args):
    return _Cond(lambda x, y: x == y, args)


def _NEq(args):
    return not _Eq(args)


def _Lt(args):
    return _Cond(lambda x, y: x < y, args)


def _Gt(args):
    return _Cond(lambda x, y: x > y, args)


def _LtE(args):
    return _Cond(lambda x, y: x <= y, args)


def _GtE(args):
    return _Cond(lambda x, y: x >= y, args)


def _Len(args):
    return sum(map(lambda x: len(x.val), args))


def _Ins(args):
    args[0].val.insert(args[1].val, args[2])
    return args[2]


def _Del(args):
    return args[0].val.pop(args[1].val)


def _Cut(args):
    return [Lit(args[0].val[:args[1].val]), Lit(args[0].val[args[1].val:])]


def _Map(args):
    return map(lambda x: args[0].Eval([x]), args[1].val)


def _Fold(args):
    return reduce(lambda x, y: args[0].Eval([x, y]), args[1].val)


def _Filter(args):
    return filter(lambda x: args[0].Eval([x]).val, args[1].val)


def _Assert(args):
    if not _Eq(args):
        print('Assert failed:', args[0], args[1])


def _Round(args):
    return int(round(args[0].val))


def _Type(args):
    return TYPES[type(args[0])]


def _Import(args):
    global CATALOG
    for arg_ in args:
        module = __import__(arg_.val)
        CATALOG.update(module.CATALOG)


CATALOG = {
    '+': _Add, '-': _Sub, '*': _Mult, '/': _Div, 'print': _Print,
    'println': _Println, '=': _Eq, '!': _NEq, '<': _Lt, '>': _Gt, '<=': _LtE,
    '>=': _GtE, 'len': _Len, 'ins': _Ins, 'del': _Del, 'cut': _Cut,
    'map': _Map, 'fold': _Fold, 'filter': _Filter, 'assert': _Assert,
    'round': _Round, 'type': _Type, 'import': _Import
}

RESERVED = [*CATALOG.keys(), 'if', 'params', 'def', 'lit']


###############################################################################
# Interpreter                                                                 #
###############################################################################

def _ExecList(val, env):
    if len(val) == 0:
        return Lit(None)
    for exp in val[:-1]:
        _Eval(exp, env)
    return _Eval(val[-1], env, True)


def _EvalList(exp, env, tail_pos=False):
    if exp[0] in CATALOG:
        return Lit(CATALOG[exp[0]](exp[1:]))
    if isinstance(exp[0], (Dict, List, String)):
        if len(exp) == 2:
            return Lit(exp[0].val[exp[1].val])
        ret = exp[0].val[exp[1].val] = exp[2]
        return ret
    if isinstance(exp[0], Function):
        return exp[0].Eval(exp[1:], tail_pos)
    raise JSOLSyntaxError('not a function name, env:', env)


def _IfBlock(exp, env, tail_pos=False):
    for i in range(0, len(exp) - 1, 2):
        if _Eval(exp[i], env).val:
            return _ExecList(exp[i + 1], env)
    if len(exp) % 2:
        return _ExecList(exp[-1], env)
    return Lit(None)


def _Eval(exp, env, tail_pos=False):
    if isinstance(exp, Type):
        return exp
    if isinstance(exp, str) and exp in CATALOG:
        return exp
    if isinstance(exp, numbers.Number):
        return Lit(exp, env)
    if isinstance(exp, dict):
        if 'lit' in exp:
            return Lit(exp['lit'], env)
        if 'def' in exp:
            return Function(exp, env)
        new_env = copy.copy(env)
        ret = Lit(None)
        for (k, v) in exp.items():
            if k in RESERVED: raise ReservedWordError(k)
            ret = env[k] = _Eval(v, new_env)
        for k in exp:
            if isinstance(env[k], Function):
                temp_env = env.copy()
                temp_env.update(env[k]._env)
                env[k]._env = temp_env
        return ret
    if isinstance(exp, list):
        name = exp[0]
        if name == 'if':
            return _IfBlock(exp[1:], env, tail_pos)
        exp = list(map(lambda x: _Eval(x, env), exp))
        if exp[0] == env and tail_pos:
            return exp, env
        try:
            result = _EvalList(exp, env, tail_pos)
            while isinstance(result, tuple):
                result = _EvalList(result[0], result[1], tail_pos)
            return result
        except Exception as e:
            raise FunctionError(e, name)
    try:
        return env[exp]
    except Exception as e:
        raise UnboundVariableError(e)


def Eval(json_dict, **kwargs):
    env = {}
    if kwargs:
        json_dict.update(kwargs)
    try:
        _Eval(json_dict, env)
        return env['main'].Eval([])
    except Exception as e:
        print('Exception:', e)


def main():
    if len(sys.argv) < 2:
        print('usage: jsol.py <jsol_files>')
        exit(0)
    for arg_ in sys.argv[1:]:
        with open(arg_, 'r') as file_:
            j = json.load(file_)
            Eval(j)
# if __name__ == '__main__':
#     main()


def Error(s):
    print(s)
    exit(0)


def _ParseString(code):
    buf = ''
    for i in range(len(code)):
        if code[i] == '"' and code[i - 1] != '\\':
            return code[i + 1:], {'lit': buf}
        if code[i] != '\\' or code[i - 1] == '\\':
            if code[i - 1] == '\\' and code[i] == 'n':
                buf += '\n'
                continue
            buf += code[i]


def _GetParens(code):
    val = 0
    for i in range(len(code)):
        if code[i] == '(':
            val += 1
        if code[i] == ')':
            if val == 0:
                return code[:i], code[i + 1:]
            val -= 1
    Error('No closing parens')


def _ParseCall(code, name):
    args, rest = _GetParens(code)
    args_list = []
    while len(args.strip()):
        args, arg_ = _Parse(args)
        args_list.append(arg_)
    return rest, [name] + args_list


def _ParseCond(if_list, code):
    cond, code = code.split('{', 1)
    if_list.append(_Parse(cond)[1])
    code, statements = _ParseBlock('{' + code)
    if_list.append(statements)
    return code


def _ParseIf(code):
    if_list = ['if']
    code = _ParseCond(if_list, code)
    temp, next_ = _Parse(code)
    while next_ == 'elif':
        code = temp
        _ParseCond(if_list, code)
        temp, next_ = _Parse(code)
    if next_ == 'else':
        code = temp
        code, statements = _ParseBlock(code)
        if_list.append(statements)
    return code, if_list


def _ParseBlock(code):
    code = code.lstrip()
    if code[0] != '{':
        Error('Code block must begin with "{"')
    code = code[1:]
    statements = []
    while code.lstrip()[0] != '}':
        code, statement = _Parse(code)
        statements.append(statement)
    return code.lstrip()[1:], statements


def _ParseFunction(code):
    params, rest = code.split(')', 1)
    params = params.split()
    rest, body = _ParseBlock(rest)
    return rest, {'params': params, 'def': body}


def _ParseList(code):
    statements = []
    while code.lstrip()[0] != ']':
        code, statement = _Parse(code)
        statements.append(statement)
    return code.lstrip()[1:], {'lit': statements}


def _ParseDict(code):
    code, d_list = _ParseBlock('{' + code)
    d = {}
    [d.update(x) for x in d_list]
    return code, {'lit': d}


def _GetNum(num):
    if num == 'null':
        return None
    if num.isdigit():
        return int(num)
    try:
        return float(num)
    except Exception as es:
        print(es)
        return num


def _Parse(code):
    global i
    buf = ''
    has_space = False
    for i in range(1, len(code) + 1):
        c = code[i - 1]
        if c in string.whitespace + ',;':
            has_space = True
            continue
        if has_space and buf or c in [']', '}', ')']:
            if buf == 'if':
                return _ParseIf(code[i - 1:])
            return code[i - 1:], _GetNum(buf)
        if c == ':':
            rest, result = _Parse(code[i:])
            return rest, {buf: result}
        if c == '"':
            return _ParseString(code[i:])
        if c == '(':
            if buf == 'def':
                return _ParseFunction(code[i:])
            code, call = _ParseCall(code[i:], buf)
            while len(code.lstrip()) and code.lstrip()[0] == '(':
                code, call = _ParseCall(code.lstrip()[1:], call)
            return code, call
        if c == '[':
            return _ParseList(code[i:])
        if c == '{':
            return _ParseDict(code[i:])
        buf += c
        has_space = False
    return code[i:], _GetNum(buf)


def Parse(code):
    d = {}
    while code:
        code, var = _Parse(code)
        d.update(var)
    return d


if __name__ == '__main__':
    if len(sys.argv[1:]) >= 1:
        for arg in sys.argv[1:]:
            with open(arg, 'r') as f:
                Eval(Parse(f.read()))
    else: # editor mode
        pass