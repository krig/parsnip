# Lord Parsnip

![parsnip](https://raw.githubusercontent.com/krig/parsnip/master/misc/lordparsnip.png "parsnip")

Combinatoric parser for Python.

## Example

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
