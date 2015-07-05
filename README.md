# Lord Parsnip

[![Build Status](https://travis-ci.org/krig/parsnip.svg)](https://travis-ci.org/krig/parsnip)
[![Code Climate](https://codeclimate.com/github/krig/parsnip/badges/gpa.svg)](https://codeclimate.com/github/krig/parsnip)

![parsnip](https://raw.githubusercontent.com/krig/parsnip/master/misc/lordparsnip.png "parsnip")

Combinatoric parsers for Python. Useful for writing and combining tiny
parsers, embedding micro-languages into other programs etc.

Mainly inspired by [parsec][1] and [jamon][2].

  [1]: http://www.haskell.org/haskellwiki/Parsec
  [2]: https://github.com/gsson/jamon

## Examples

### Basic matching

```python
from parsnip import *


labelled_list = seq(lift(regex(r'(\w+):')), many(regex(r'\w+')))

words = tokens("words: foo bar wiz bang")
labelled_list(words)
# => ['words', ['foo', 'bar', 'wiz', 'bang']]


labelled_dict = mapfn(labelled_list, lambda a: {a[0]: a[1]})

words = tokens("words: foo bar wiz bang")
labelled_dict(words)
# => {'words': ['foo', 'bar', 'wiz', 'bang']}


malformed = tokens("foo bar wiz bang")
labelled_dict(malformed)
# =>
#   NoMatch: Input: foo, Expected: (\w+): [\w+ ...]
#	    Caused by: Input: foo, Expected: (\w+):

```

### Lexing

```python
from parsnip import *

lexer = regex_lexer(r'\(', r'\)', '{', '}', ',', '[a-zA-Z_][a-zA-Z0-9_]*',
                    skip=r'[\s\n]+')
name = regex('\w+', '<name>')
arg = regex('[a-zA-z][a-zA-Z0-9_]*', '<arg>')
arglist = lift2(seq(text('('), sep(arg, text(',')), text(')')))
body = lift2(seq(text('{'), text('pass'), text('}')))

fundef = seq(text('def'), name, arglist, body)

print fundef.__doc__
# => def <name> ( [<arg> [, <arg>] ...] ) { pass }

print fundef(tokens(lexer("""
def foo(x, y, z) {
    pass
}
""")))
# => ['def', 'foo', ['x', 'y', 'z'], 'pass']
```

### Tagging

```python

# Using parsers from previous example...

fundef = seq(text('def'),
    tag(name, 'name'),
    tag(arglist, 'args'),
    tag(body, 'body'))

fundef = maptags(fundef, lambda tags: tags)

print fundef(tokens(lexer("""
def foo(x, y, z) {
    pass
}
""")))

# => {'name': 'foo',
#     'args': ['x', 'y', 'z'],
#     'body': 'pass'}

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
* `tagfn(parser, name, fn)` - pass output of _parser_ through _fn_ and store in tag _name_
* `maptags(parser, fn)` - when matched, _fn_ is called with a `dict` of tags as parameter

## Mapping

* `mapfn(parser, fn)` - when matched, _fn_ is called with output of _parser_ as parameter

## Lifting

* `lift(parser)` - return first element of list returned by _parser_ as result
* `lift2(parser)` - return second element of list returned by _parser_ as result

## Tokenizers

* `tokens(x)` - return a token stream using _x_ as source
* `tokens_list(list)` - _list_ is a list of tokens
* `tokens_shlex(str)` - _str_ is tokenized using `shlex.split`
* `tokens_text(str)` - _str_ is tokenized using `string.split`
* `regex_lexer(*regexes, [skip=regex])` - returns a token generator by matching regexes
* `tokens_gen(generator)` - generate list of tokens from generator
