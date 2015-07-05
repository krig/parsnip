import re
from contextlib import contextmanager
from functools import wraps
from inspect import getdoc

from .errors import NoMatch
from .tokens import END


@contextmanager
def _savestate(tokens):
    tmp = tokens._curr
    try:
        yield
    except NoMatch:
        tokens._curr = tmp


def parsnip(doc=None):
    def parsnip2(parser):
        parser.__doc__ = doc

        @wraps(parser)
        def run(tokens):
            try:
                return parser(tokens)
            except NoMatch as e:
                if e.expected == parser.__doc__ or e.passthrough:
                    raise e
                raise NoMatch(got=e.got,
                              expected=parser.__doc__,
                              caused_by=e if e.expected else None)
        return run
    return parsnip2


def text(txt):
    "leaf parser: matches text case-insensitively"
    txt = txt.lower()

    @parsnip(doc=txt)
    def ptext(tok):
        v = tok.next().lower()
        if v == txt:
            return v
        raise NoMatch(v)
    return ptext


def regex(rx, doc=None, flags=re.I):
    "leaf parser: matches regex"
    if isinstance(rx, basestring):
        if not rx.endswith('$'):
            rx = rx + '$'
        c = re.compile(rx, flags=flags)
    else:
        c = rx

    @parsnip(doc=doc or c.pattern.rstrip('$'))
    def pregex(tok):
        v = tok.next()
        m = c.match(v)
        if m and m.groups():
            return m.groups()
        elif m:
            return m.string
        raise NoMatch(v)
    return pregex


def seq(*parsers):
    "match all in sequence"
    def pseq(tok):
        ret = []
        start = tok._curr
        for p in parsers:
            try:
                ret.append(p(tok))
            except NoMatch as e:
                prevtok = tok.getTokens(start, start + len(ret))
                got = ' '.join(prevtok + [str(tok.peekCurrent())])
                expected = ' '.join(prevtok + [p.__doc__])
                raise NoMatch(got=got,
                              expected=expected,
                              caused_by=e)
        return ret
    pseq.__doc__ = " ".join(getdoc(p) for p in parsers)
    return pseq


def lift(parser):
    "lifts the first return value of parser"
    @parsnip(doc=getdoc(parser))
    def plift(tok):
        r = parser(tok)
        if r is None:
            return r
        return r[0]
    return plift


def lift2(parser):
    "lifts the second return value of parser"
    @parsnip(doc=getdoc(parser))
    def plift2(tok):
        return parser(tok)[1]
    return plift2


def liftNth(parser, n):
    "lifts the Nth return value of parser"
    @parsnip(doc=getdoc(parser))
    def pliftNth(tok):
        return parser(tok)[n]
    return pliftNth


def choice(*parsers):
    "try to match all until one matches"
    @parsnip(doc='(%s)' % (" | ".join(getdoc(p) for p in parsers)))
    def pchoice(tok):
        for p in parsers:
            with _savestate(tok):
                return p(tok)
        raise NoMatch(tok.next())
    return pchoice


def choiceConsumeAll(*parsers):
    """
    try to match until one matches.
    if a match is partial but doesn't consume all tokens,
    this fails
    """
    @parsnip(doc='(%s)' % (" | ".join(getdoc(p) for p in parsers)))
    def pchoice(tok):
        longest_match = (0, None)
        tok.resetLongestMatch()
        for p in parsers:
            try:
                ret = p(tok)
                if not tok.empty():
                    mplus = tok.next()
                    prevtok = tok.getTokens(*tok.getLongestMatch())
                    got = ' '.join(prevtok + [str(mplus)])
                    raise NoMatch(got=got,
                                  expected=getdoc(p) + ' <END>',
                                  passthrough=True)
                return ret
            except NoMatch as e:
                if e.passthrough:
                    raise e
                lf, lt = tok.getLongestMatch()
                nmatch = lt - lf
                if nmatch > longest_match[0]:
                    prevtok = tok.getTokens(lf, lt)
                    got = ' '.join(prevtok + [str(tok.peekCurrent())])
                    expected = p.__doc__
                    longest_match = (nmatch,
                                     NoMatch(got=got,
                                             expected=expected,
                                             caused_by=e))
                tok._curr = lf
        if longest_match[1]:
            longest_match[1].passthrough = True
            raise longest_match[1]
        else:
            raise NoMatch(tok.next())
    return pchoice


def option(p, value=None):
    "always succeeds, if p doesn't match, value is returned as match"
    @parsnip(doc='[%s]' % (getdoc(p)))
    def poption(tok):
        with _savestate(tok):
            return p(tok)
        return value
    return poption


def matchNM(p, n, m):
    "match between N and M instances of p"
    @parsnip(doc='%s{%d,%d}' % (getdoc(p), n, m))
    def pmatchNM(tok):
        if n == 0:
            ret = []
        else:
            ret = [p(tok) for _ in xrange(0, n)]
        for _ in xrange(n, m):
            with _savestate(tok):
                ret.append(p(tok))
                continue
            break
        return ret
    return pmatchNM


def exactlyN(p, n):
    "match exactly N instances of p"
    @parsnip(doc='%s{%d}' % (getdoc(p), n))
    def pexactlyN(tok):
        return [p(tok) for _ in xrange(0, n)]
    return pexactlyN


def tag(p, name):
    "tags match from p with name"
    @parsnip(doc=getdoc(p))
    def ptag(tok):
        ret = p(tok)
        tok.set_tag(name, ret)
        return ret
    return ptag


def tagfn(p, name, fn):
    "saves output of fn(val) in tag"
    @parsnip(doc=getdoc(p))
    def ptagfn(tok):
        ret = p(tok)
        tok.set_tag(name, fn(ret))
        return ret
    return ptagfn


def mapfn(parser, fn):
    """pass output from parser through fn
    and use that instead"""
    @parsnip(doc=getdoc(parser))
    def pmapfn(tok):
        return fn(parser(tok))
    return pmapfn


def maptags(parser, fn):
    """discard output from parser, pass
    tag dict to fn and use output as result"""
    @parsnip(doc=getdoc(parser))
    def pmaptags(tok):
        parser(tok)
        return fn(tok.tags)
    return pmaptags


def loopref(name):
    """returns a loop reference used to backpatch
    recursive grammars"""
    @parsnip(doc=name)
    def ploopref(tok):
        return ploopref.func_dict['loop'](tok)
    ploopref.func_dict['loop'] = None
    return ploopref


def loop(parser, ref):
    "enables parser as a recursive parser that can loop on itself"
    ref.func_dict['loop'] = parser
    return parser


def many(p, min=0):
    "match several p's, but at least <min>"
    def manydoc():
        if min == 0:
            return '[%s ...]' % (getdoc(p))
        else:
            return '%s ...' % (getdoc(p))

    @parsnip(doc=manydoc())
    def pmany(tok):
        acc = []
        while True:
            with _savestate(tok):
                v = p(tok)
                acc.append(v)
                continue
            if len(acc) < min:
                raise NoMatch(got=tok.peekNext())
            break
        return acc
    return pmany


def many1(p):
    "match one or more p"
    return many(p, min=1)


def unless(p):
    "if p matches, this fails"
    @parsnip(doc="!%s" % (getdoc(p)))
    def punless(tok):
        try:
            ret = p(tok)
        except NoMatch as e:
            return e.got
        raise NoMatch(ret)
    return punless


def manyTill(p):
    "matches zero or more tokens until p succeeds or all tokens are consumed"
    return many(unless(p))


def manyAndTill(p):
    """matches zero or more tokens until p succeeds,
    then matches p as well (so end sentinel is consumed)"""
    return seq(many(unless(p)), p)


def sep(parser, separator):
    @parsnip(doc='[%s [%s %s] ...]' % (getdoc(parser), getdoc(separator), getdoc(parser)))
    def psep(tok):
        acc = []
        with _savestate(tok):
            v = parser(tok)
            acc.append(v)
        if not acc:
            return acc
        while True:
            with _savestate(tok):
                separator(tok)
            with _savestate(tok):
                v = parser(tok)
                acc.append(v)
                continue
            break
        return acc
    return psep


def anything():
    "match ...anything."
    @parsnip(doc='*')
    def panything(tok):
        return tok.next()
    return panything


def end():
    "match the end of input"
    @parsnip(doc=str(END))
    def pend(tok):
        if not tok.empty():
            raise NoMatch(tok.next())
        return END
    return pend


def wrap(*args):
    """
    == seq(text(left), *p, text(right))
    """
    args = list(args)
    args[0] = text(args[0])
    args[-1] = text(args[-1])
    return seq(*args)


def doc(parser, text):
    """
    Replace documentation for parser with the given text
    """
    parser.__doc__ = text
    return parser


def parse(parser, ts):
    """
    Invokes the given parser on the given
    token stream.
    """
    return parser(ts)
