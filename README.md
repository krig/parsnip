# Lord Parsnip

![parsnip](https://raw.githubusercontent.com/krig/parsnip/master/misc/lordparsnip.png "parsnip")

Combinatoric parser for Python.

## Examples

```python
from parsnip import seq, regex, many, tokens_text

labelled_list = seq(lift(regex(r'(\w+):')), many(regex(r'\w+')))

labelled_list(tokens_text("words: foo bar wiz bang"))
# => ['words', ['foo', 'bar', 'wiz', 'bang']]

labelled_list(tokens_text("words foo bar wiz bang"))
# =>
#   NoMatch: Input: words, Expected: (\w+):
#     Caused by: Input: words, Expected: (\w+):
```

```python
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

print parser.__doc__
# => def <name> ( [<arg> [, <arg>] ...] ) { pass }

print parser(tokens_gen(lexer("""
def foo(x, y, z) {
    pass
}
""")))
# => ['def', 'foo', ['x', 'y', 'z'], 'pass']
```

# Documentation

## Basic parsers

* `text(str)` - matches _str_ (case-insensitive)
* `regex(txt, [doc], [flags])` - matches the regular expression _txt_
* `anything()` - match anything
* `end()` - match the end of input
* `doc(parser, text)` - rename _parser_ as _text_

## Combinations

* `option(parser)` - optionally matches _parser_
* `seq(*parsers)` - matches an exact sequence of _parsers_
* `many(parser)` - matches _parser_ zero or more times
* `many1(parser)` - matches _parser_ one or more times
* `choice(*parsers)` - matches one of _parsers_
* `exactlyN(parser, n)` - matches _parser_ exactly _n_ times
* `matchNM(parser, n, m)` - matches _parser_ exactly _n_-_m_ times
* `unless(parser)` - fail if _parser_ matches
* `manyTill(parser)` - match zero or more tokens until _parser_ matches
* `manyAndTill(parser)` - match zero or more tokens until _parser_ matches, then match _parser_ as well
* `sep(parser, separator)` - match instances of _parser_ separated by _separator_
* `wrap(first, *parsers, then)` - `seq(text(first), *parsers, text(then))`

## Loops

* `loopref(name)` - create a named loop reference
* `loop(parser, ref)` - enable recursion over _parser_ via _ref_

## Tagging

* `tag(parser, name)` - store output of _parser_ in tag _name_
* `tagfn(parser, fn)` - when matched, _fn_ is called with a `dict` of tags as parameter

## Mapping

* `mapfn(parser, fn)` - when matched, _fn_ is called with output of _parser_ as parameter

## Lifting

* `lift(parser)` - return first element of list returned by _parser_ as result
* `lift2(parser)` - return second element of list returned by _parser_ as result

## Tokenizers

* `tokens_list(list)` - _list_ is a list of tokens
* `tokens_shlex(str)` - _str_ is tokenized using `shlex.split`
* `tokens_text(str)` - _str_ is tokenized using `string.split`
* `regex_lexer(*regexes, [skip=regex])` - returns a token generator by matching regexes
* `tokens_gen(generator)` - generate list of tokens from generator
