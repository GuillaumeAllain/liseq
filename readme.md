# LISEQ

Liseq is a s-expr to CODEV macro-plus transpiler. Since the scripting language for CODEV is bare-bones, a lot of boilerplate code is needed for simple functionnality. The scope of this transpiler is to offer a transparent way to write macro-plus sequence files with added functionnality to write less noisy source code.

The s-expr syntax is loosely based on lisp. The project is still a rough work-in progress, so functionnality may drastically change in the future.

## Installation

Clone and install with

``` console
foo@bar:liseq$ pip install .
```


or

``` console
foo@bar:liseq$ pip install git+https://github.com/GuillaumeAllain/liseq.git
```


## Quick documentation

The main command for calling the transpiler on a file:

```
liseq file.liseq -o file.seq
```

Without specifying the `-o` option, the compiled *.seq file will be printed on stdout. The transpiler is also available from python by 

``` python
from liseq.core import transpiler
```

### Variable assigment

``` lisp
(var num foo 10)
```


compiles to

``` code
lcl num ^foo
^foo == 10
```


### Function call

``` lisp
(concat arg1 "arg2")
```


compiles to

``` code
concat(^arg1, "arg2")
```


### If statement

``` lisp
(if (== foobar 1) (wri "bar") (== foobar 2) (wri "barbar") (wri "barbarbar"))
```


compiles to

``` code
if ^foobar = 1
    wri "bar"
else if ^foobar = 2
    wri "barbar"
else
    wri "barbarbar"
end if
```


### For loop

``` lisp
(for [i 1 10 2] (wri "loop:" i))
```


compiles to

``` code
for ^i 1 10 2
    wri "loop:" ^i
end for
```


### database access

``` lisp
(eva x r1)
```


compiles to

``` code
(x r1)
```


### Subprogram call (WIP)

``` lisp
(vie s1..3 (lab n))
```


compile to

    vie;s1..3;lab n; go

## TODO

-   [ ] Documentation
-   [ ] Function support
-   [ ] Helper for graphics
