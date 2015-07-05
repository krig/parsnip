import re

from .errors import NoMatch


class __EndSentinel(object):
    def __repr__(self):
        return '<END>'

END = __EndSentinel()


class TokenStream(object):
    def __init__(self, tokens):
        self._tokens = tokens
        self._curr = 0
        self.tags = {}
        self.result = None
        self._longest = [-1, -1]

    def next(self):
        "the next token"
        if self.empty():
            raise NoMatch(END)
        if self._longest[1] < self._curr:
            self._longest[1] = self._curr
        self._curr += 1
        return self._tokens[self._curr - 1]

    def peekCurrent(self):
        if self._curr == 0:
            return ""
        return self._tokens[self._curr - 1]

    def peekNext(self):
        if self._curr >= len(self._tokens):
            return END
        return self._tokens[self._curr]

    def resetLongestMatch(self):
        self._longest = [self._curr, self._curr]

    def getLongestMatch(self):
        return self._longest

    def all(self):
        return self._tokens

    def getTokens(self, s, e):
        "returns tokens[s:e] (not inclusive)"
        return self._tokens[s:e]

    def empty(self):
        "true if there are no more tokens"
        return self._curr >= len(self._tokens)

    def set_tag(self, name, value):
        "tags the given value"
        if name in self.tags:
            raise SyntaxError("Ambiguous tag '%s', already set to %s" % (name, self.tags[name]))
        self.tags[name] = value

    def tag(self, name, defval=None):
        return self.tags.get(name, defval)


def tokens_list(lst):
    """
    Returns token stream for list of tokens
    """
    return TokenStream(lst)


def tokens_shlex(txt):
    """
    Splits string into tokens using shlex.split
    """
    import shlex
    return TokenStream(shlex.split(txt))


def tokens_text(txt):
    """
    Splits string into tokens using string.split()
    """
    return TokenStream(txt.split())


def regex_lexer(*rx, **kwargs):
    """
    Splits string using a list of regexes
    special regex [0] matches whitespace
    """
    skip = re.compile(kwargs.get('skip', r'\s+'))
    rx = [re.compile(r) for r in rx]

    def tokens(t):
        while t:
            m = skip.match(t)
            if m:
                t = t[m.end():]
                continue
            for r in rx:
                m = r.match(t)
                if m:
                    yield t[0:m.end()]
                    t = t[m.end():]
                    break
            else:
                raise ValueError("No match for token: %s" % (repr(t[0])))
    return tokens


def tokens_gen(g):
    """
    Takes a token generator or a list
    """
    return TokenStream([x for x in g])


def tokens(x):
    """
    Try to guess what type of token stream this is
    """
    if isinstance(x, basestring):
        return tokens_text(x)
    elif isinstance(x, list):
        return tokens_list(x)
    elif isinstance(x, TokenStream):
        return x
    else:
        return tokens_gen(x)
