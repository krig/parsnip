import nose.tools as tools

from parsnip import NoMatch
from parsnip import text, regex
from parsnip import seq, sep
from parsnip import lift2
from parsnip import regex_lexer
from parsnip import tokens, tokens_shlex
from parsnip import tag, maptags

def test_text():
    parser = text('foo')
    tools.eq_(parser(tokens_shlex('foo')), 'foo')


@tools.raises(NoMatch)
def test_text_mismatch():
    parser = text('foo')
    parser(tokens_shlex('bar'))


def test_example():
    lexer = regex_lexer(r'\(', r'\)', '{', '}', ',', '[a-zA-Z_][a-zA-Z0-9_]*',
                        skip=r'[\s\n]+')
    arg = regex('[a-zA-z][a-zA-Z0-9_]*', '<arg>')
    arglist = lift2(seq(text('('), sep(arg, text(',')), text(')')))
    body = lift2(seq(text('{'), text('pass'), text('}')))
    parser = seq(text('def'),
                 regex('\w+', '<name>'),
                 arglist,
                 body)

    out = parser(tokens(lexer("""
    def foo(x, y, z) {
        pass
    }
    """)))
    tools.eq_(out, ['def', 'foo', ['x', 'y', 'z'], 'pass'])


def test_tagging():
    name = regex('\w+', '<name>')
    lexer = regex_lexer(r'\(', r'\)', '{', '}', ',', '[a-zA-Z_][a-zA-Z0-9_]*',
                        skip=r'[\s\n]+')
    arg = regex('[a-zA-z][a-zA-Z0-9_]*', '<arg>')
    arglist = lift2(seq(text('('), sep(arg, text(',')), text(')')))
    body = lift2(seq(text('{'), text('pass'), text('}')))

    fundef = seq(text('def'),
                 tag(name, 'name'),
                 tag(arglist, 'args'),
                 tag(body, 'body'))

    fundef = maptags(fundef, lambda tags: tags)

    out = fundef(tokens(lexer("""
    def funfunc(x, y, z) {
        pass
    }
    """)))

    tools.eq_(out['name'], 'funfunc')
    tools.eq_(out['args'][0], 'x')
    tools.eq_(out['body'], 'pass')
