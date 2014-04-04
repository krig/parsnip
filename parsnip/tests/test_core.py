import parsnip as p
import nose.tools as tools


def test_text():
    parser = p.text('foo')
    tools.eq_(parser(p.tokens_shlex('foo')), 'foo')


@tools.raises(p.NoMatch)
def test_text_mismatch():
    parser = p.text('foo')
    parser(p.tokens_shlex('bar'))


def test_example():
    from parsnip import text, lift2, regex, sep, seq, tokens_gen, regex_lexer
    lexer = regex_lexer(r'\(', r'\)', '{', '}', ',', '[a-zA-Z_][a-zA-Z0-9_]*',
                        skip=r'[\s\n]+')
    arg = regex('[a-zA-z][a-zA-Z0-9_]*', '<arg>')
    arglist = lift2(seq(text('('), sep(arg, text(',')), text(')')))
    body = lift2(seq(text('{'), text('pass'), text('}')))
    parser = seq(text('def'),
                 regex('\w+', '<name>'),
                 arglist,
                 body)

    out = parser(tokens_gen(lexer("""
    def foo(x, y, z) {
        pass
    }
    """)))
    tools.eq_(out, ['def', 'foo', ['x', 'y', 'z'], 'pass'])
