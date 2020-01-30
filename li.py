#!/usr/bin/env python

from functools import reduce
import copy
import json
import numbers
import sys
from os import open as os_open, O_RDWR as os_O_RDWR, read as os_read, write as os_write, close as os_close
import string


class Li:
    def __init__(self):
        self.TYPES = {
            self.LiList: "LiList",
            self.LiDict: "LiDict",
            self.LiString: "LiString",
            self.LiNumber: "LiNumber",
            self.LiFunction: "LiFunction",
            self.LiNull: "LiNull"
        }

        self.NoneType = type(None)

        self.LITERALS = {
            list: self.LiList,
            dict: self.LiDict,
            str: self.LiString,
            int: self.LiNumber,
            bool: self.LiNumber,
            float: self.LiNumber,
            self.NoneType: self.LiNull,
        }

        self.CATALOG = {
            'open': self.li_open, 'read': self.li_read, 'write': self.li_write, 'close': self.li_close,
            '+': self._Add, '-': self._Sub, '*': self._Mult, '/': self._Div, 'print': self._Print,
            'println': self._Println, '=': self._Eq, '!': self._NEq, '<': self._Lt, '>': self._Gt, '<=': self._LtE,
            '>=': self._GtE, 'len': self._Len, 'ins': self._Ins, 'del': self._Del, 'cut': self._Cut,
            'map': self._Map, 'fold': self._Fold, 'filter': self._Filter, 'assert': self._Assert,
            'round': self._Round, 'type': self._Type, 'import': self._Import
        }

        self.RESERVED = [*self.CATALOG.keys(), 'if', 'params', 'def', 'lit']

    # > Extras functions                                                           #
    # ------------------------------------------------------------------------------
    def li_open(self, args):
        return os_open(args[0].val.strip(), os_O_RDWR)

    def li_read(self, args):
        return os_read(args[0].val, args[1].val)

    def li_write(self, args):
        return os_write(args[0].val, args[1].val)

    def li_close(self, args):
        return os_close(args[0].val)

    # > Errors                                                                     #
    # ------------------------------------------------------------------------------

    class Error(Exception):
        pass

    class LiLiFunctionError(Error):
        def __init__(self, e, name):
            self.name = name.__str__()
            self.e = e

        def __str__(self):
            return self.name + ': ' + self.e.__str__()

    class LiUnboundVariableError(Error):
        def __init__(self, e):
            self.e = e

        def __str__(self):
            return 'unbound variable: ' + self.e.__str__()

    class LiSyntaxError(Error):
        def __init__(self, msg):
            self.msg = msg

        def __str__(self):
            return self.msg

    class LiReservedWordError(Error):
        def __init__(self, word):
            self.word = word

        def __str__(self):
            return self.word + ' is a reserved word'

    # > Types                                                                       #
    # -----------------------------------------------------------------------------

    class Type(object):
        pass

    class LiLiteral(Type):
        def __init__(self, val, env):
            self.env = env
            self.val = copy.copy(val)

        def __eq__(self, o):
            return self.val == o.val

        def __str__(self):
            return str(self.val)

        def json(self):
            return dict([('lit', self.val)])

    class LiList(LiLiteral):
        def __init__(self, val, env):
            super(self.LiList, self).__init__(val, env)
            for (i, v) in enumerate(self.val):
                self.val[i] = self._Eval(v, env)

        def __str__(self):
            return str(map(lambda x: x.__str__(), self.val))

        def json(self):
            return dict([('lit', map(lambda x: x.json(), self.val))])

    class LiDict(LiLiteral):
        def __init__(self, val, env):
            super(self.LiDict, self).__init__(val, env)
            dict_env = env.copy()
            for (k, v) in self.val.iteritems():
                self.val[k] = self._Eval(v, dict_env)
            for v in self.val.values():
                if isinstance(v, self.LiFunction):
                    v._env = self.val

        def json(self):
            return dict([('lit',
                          dict(zip(self.val.keys(),
                                   map(lambda x: x.json(), self.val.values()))))])

    class LiString(LiLiteral):
        pass

    class LiNumber(LiLiteral):
        def json(self):
            return self.val

    class LiNull(LiLiteral):
        def json(self):
            return self.val

        def __str__(self):
            return 'LiNull'

    class LiFunction(Type):
        class _LiFunctionEnv(object):
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
            li = Li()
            return li._ExecLiList(
                self._def,
                self._LiFunctionEnv(self._env, dict(zip(self._params, args)), self))

    def Lit(self, val, env=None):
        if env is None:
            env = {}
        if isinstance(val, self.Type):
            return val
        return self.LITERALS[type(val)](val, env)

    # > Built-in LiFunctions                                                      #
    # -----------------------------------------------------------------------------

    def _Cond(self, func, val):
        return all(func(val[i].val, val[i + 1].val) for i in range(len(val) - 1))

    def _Add(self, args):
        return reduce(lambda x, y: self.Lit(x.val + y.val), args)

    def _Sub(self, args):
        return reduce(lambda x, y: self.Lit(x.val - y.val), args)

    def _Mult(self, args):
        return reduce(lambda x, y: self.Lit(x.val * y.val), args)

    def _Div(self, args):
        return reduce(lambda x, y: self.Lit(x.val / y.val), args)

    def _Println(self, args):
        for arg_ in args:
            print(arg_)

    def _Print(self, args):
        for arg_ in args:
            sys.stdout.write(arg_.__str__())
        sys.stdout.flush()

    def _Eq(self, args):
        return self._Cond(lambda x, y: x == y, args)

    def _NEq(self, args):
        return not self._Eq(args)

    def _Lt(self, args):
        return self._Cond(lambda x, y: x < y, args)

    def _Gt(self, args):
        return self._Cond(lambda x, y: x > y, args)

    def _LtE(self, args):
        return self._Cond(lambda x, y: x <= y, args)

    def _GtE(self, args):
        return self._Cond(lambda x, y: x >= y, args)

    def _Len(self, args):
        return sum(map(lambda x: len(x.val), args))

    def _Ins(self, args):
        args[0].val.insert(args[1].val, args[2])
        return args[2]

    def _Del(self, args):
        return args[0].val.pop(args[1].val)

    def _Cut(self, args):
        return [self.Lit(args[0].val[:args[1].val]), self.Lit(args[0].val[args[1].val:])]

    def _Map(self, args):
        return map(lambda x: args[0].Eval([x]), args[1].val)

    def _Fold(self, args):
        return reduce(lambda x, y: args[0].Eval([x, y]), args[1].val)

    def _Filter(self, args):
        return filter(lambda x: args[0].Eval([x]).val, args[1].val)

    def _Assert(self, args):
        if not self._Eq(args):
            print('Assert failed:', args[0], args[1])

    def _Round(self, args):
        return int(round(args[0].val))

    def _Type(self, args):
        return self.TYPES[type(args[0])]

    def _Import(self, args):
        for arg_ in args:
            module = __import__(arg_.val)
            self.CATALOG.update(module.CATALOG)

    ###############################################################################
    # Interpreter                                                                 #
    ###############################################################################

    def _ExecLiList(self, val, env):
        if len(val) == 0:
            return self.Lit(None)
        for exp in val[:-1]:
            self._Eval(exp, env)
        return self._Eval(val[-1], env, True)

    def _EvalLiList(self, exp, env, tail_pos=False):
        if exp[0] in self.CATALOG:
            return self.Lit(self.CATALOG[exp[0]](exp[1:]))
        if isinstance(exp[0], (self.LiDict, self.LiList, self.LiString)):
            if len(exp) == 2:
                return self.Lit(exp[0].val[exp[1].val])
            ret = exp[0].val[exp[1].val] = exp[2]
            return ret
        if isinstance(exp[0], self.LiFunction):
            return exp[0].Eval(exp[1:], tail_pos)
        raise self.LiSyntaxError('not a function name, env:', env)

    def _IfBlock(self, exp, env, tail_pos=False):
        for i in range(0, len(exp) - 1, 2):
            if self._Eval(exp[i], env).val:
                return self._ExecLiList(exp[i + 1], env)
        if len(exp) % 2:
            return self._ExecLiList(exp[-1], env)
        return self.Lit(None)

    def _Eval(self, exp, env, tail_pos=False):
        li = Li()
        if isinstance(exp, self.Type):
            return exp
        if isinstance(exp, str) and exp in li.CATALOG:
            return exp
        if isinstance(exp, numbers.Number):
            return self.Lit(exp, env)
        if isinstance(exp, dict):
            if 'lit' in exp:
                return self.Lit(exp['lit'], env)
            if 'def' in exp:
                return self.LiFunction(exp, env)
            new_env = copy.copy(env)
            ret = self.Lit(None)
            for (k, v) in exp.items():
                if k in self.RESERVED: raise self.LiReservedWordError(k)
                ret = env[k] = self._Eval(v, new_env)
            for k in exp:
                if isinstance(env[k], self.LiFunction):
                    temp_env = env.copy()
                    temp_env.update(env[k]._env)
                    env[k]._env = temp_env
            return ret
        if isinstance(exp, list):
            name = exp[0]
            if name == 'if':
                return self._IfBlock(exp[1:], env, tail_pos)
            exp = list(map(lambda x: self._Eval(x, env), exp))
            if exp[0] == env and tail_pos:
                return exp, env
            try:
                result = self._EvalLiList(exp, env, tail_pos)
                while isinstance(result, tuple):
                    result = self._EvalLiList(result[0], result[1], tail_pos)
                return result
            except Exception as e:
                raise self.LiLiFunctionError(e, name)
        try:
            return env[exp]
        except Exception as e:
            raise self.LiUnboundVariableError(e)

    def Eval(self, json_dict, **kwargs):
        env = {}
        if kwargs:
            json_dict.update(kwargs)
        try:
            self._Eval(json_dict, env)
            return env['main'].Eval([])
        except Exception as e:
             print('Exception:', e)

    def Error(self, s):
        print(s)
        exit(0)

    def _ParseLiString(self, code):
        buf = ''
        for i in range(len(code)):
            if code[i] == '"' and code[i - 1] != '\\':
                return code[i + 1:], {'lit': buf}
            if code[i] != '\\' or code[i - 1] == '\\':
                if code[i - 1] == '\\' and code[i] == 'n':
                    buf += '\n'
                    continue
                buf += code[i]

    def _GetParens(self, code):
        val = 0
        for i in range(len(code)):
            if code[i] == '(':
                val += 1
            if code[i] == ')':
                if val == 0:
                    return code[:i], code[i + 1:]
                val -= 1
        self.Error('No closing parens')

    def _ParseCall(self, code, name):
        args, rest = self._GetParens(code)
        args_list = []
        while len(args.strip()):
            args, arg_ = self._Parse(args)
            args_list.append(arg_)
        return rest, [name] + args_list

    def _ParseCond(self, if_list, code):
        cond, code = code.split('{', 1)
        if_list.append(self._Parse(cond)[1])
        code, statements = self._ParseBlock('{' + code)
        if_list.append(statements)
        return code

    def _ParseIf(self, code):
        if_list = ['if']
        code = self._ParseCond(if_list, code)
        temp, next_ = self._Parse(code)
        while next_ == 'elif':
            code = temp
            self._ParseCond(if_list, code)
            temp, next_ = self._Parse(code)
        if next_ == 'else':
            code = temp
            code, statements = self._ParseBlock(code)
            if_list.append(statements)
        return code, if_list

    def _ParseBlock(self, code):
        code = code.lstrip()
        if code[0] != '{':
            self.Error('Code block must begin with "{"')
        code = code[1:]
        statements = []
        while code.lstrip()[0] != '}':
            code, statement = self._Parse(code)
            statements.append(statement)
        return code.lstrip()[1:], statements

    def _ParseLiFunction(self, code):
        params, rest = code.split(')', 1)
        params = params.split()
        rest, body = self._ParseBlock(rest)
        return rest, {'params': params, 'def': body}

    def _ParseLiList(self, code):
        statements = []
        while code.lstrip()[0] != ']':
            code, statement = self._Parse(code)
            statements.append(statement)
        return code.lstrip()[1:], {'lit': statements}

    def _ParseLiDict(self, code):
        code, d_list = self._ParseBlock('{' + code)
        d = {}
        [d.update(x) for x in d_list]
        return code, {'lit': d}

    def _GetNum(self, num):
        if num == 'null':
            return None
        if num.isdigit():
            return int(num)
        try:
            return float(num)
        except Exception as es:
            print(es)
            return num

    def _Parse(self, code):
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
                    return self._ParseIf(code[i - 1:])
                return code[i - 1:], self._GetNum(buf)
            if c == ':':
                rest, result = self._Parse(code[i:])
                return rest, {buf: result}
            if c == '"':
                return self._ParseLiString(code[i:])
            if c == '(':
                if buf == 'def':
                    return self._ParseLiFunction(code[i:])
                code, call = self._ParseCall(code[i:], buf)
                while len(code.lstrip()) and code.lstrip()[0] == '(':
                    code, call = self._ParseCall(code.lstrip()[1:], call)
                return code, call
            if c == '[':
                return self._ParseLiList(code[i:])
            if c == '{':
                return self._ParseLiDict(code[i:])
            buf += c
            has_space = False
        return code[i:], self._GetNum(buf)

    def Parse(self, code):
        d = {}
        while code:
            code, var = self._Parse(code)
            d.update(var)
        return d


if __name__ == '__main__':
    if len(sys.argv[1:]) >= 1:
        li = Li()
        for arg in sys.argv[1:]:
            with open(arg, 'r') as f:
                li.Eval(li.Parse(f.read()))
    else:  # editor mode
        pass
