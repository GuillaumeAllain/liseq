---
lang: en_us
---

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


## Brief documentation

The main command for calling the transpiler on a file:

    liseq file.liseq -o file.seq

Without specifying the `-o` option, the compiled \*.seq file will be printed on stdout. The transpiler is also available from python with

``` python
from liseq.core import transpiler
```


### Variable definition

``` lisp
(num foo (nth bar 3))
```


compiles to

``` code
lcl num ^foo ^bar(3)
```


### Variable assignement

``` lisp
(set (num foo) 3)
(set (nth 2 bar) 3)
```


compiles to

``` code
lcl num ^foo
^foo == 3
^bar(2) ==3
```


### Function call

``` lisp
(concat (var arg1) "arg2")
```


compiles to

``` code
concat(^arg1, "arg2")
```


### If statement

``` lisp
(if (== (var foobar) 1) (wri "bar") (== (var foobar) 2) (wri "barbar") (wri "barbarbar"))
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
(for [i 1 10 2] (wri "loop:" (var i)))
```


compiles to

``` code
for ^i 1 10 2
    wri "loop:" ^i
end for
```


### database access

``` lisp
(database x r1)
```


compiles to

``` code
(x r1)
```


### Options call

``` lisp
(option vie [(sur (to s1 3)) (lab n)])
```


compiles to

``` code
vie;sur s1..3;lab n; go
```


### Function definition

``` lisp
(fn function_name [(num arg1) (num arg2)]
  [(set (num output) (+ arg1 arg2))]
  output)
```


compiles to

``` code
dro fct @function_name
ope new U^filefunctemp "cvtempfunc94b5d143a12558bb414813edae566d2e.seq"
wri U^filefunctemp 'if (out)'
wri U^filefunctemp '^__suppress_orig_out == "y"'
wri U^filefunctemp 'else'
wri U^filefunctemp '^__suppress_orig_out == "n"'
wri U^filefunctemp 'end if'
wri U^filefunctemp 'if (^__suppress_orig_out <> "n")'
wri U^filefunctemp 'out n'
wri U^filefunctemp 'end if'
wri U^filefunctemp 'if (ver)'
wri U^filefunctemp '^__suppress_orig_ver == "y"'
wri U^filefunctemp 'else'
wri U^filefunctemp 'ver n'
wri U^filefunctemp 'end if'
wri U^filefunctemp 'fct @function_name(num ^arg1, num ^arg2)'
wri U^filefunctemp 'num ^output'
wri U^filefunctemp '^output == (arg1 + arg2)'
wri U^filefunctemp 'end fct ^output'
wri U^filefunctemp 'lbl __codev_end'
wri U^filefunctemp 'if (^__suppress_orig_out <> "n")'
wri U^filefunctemp 'out y'
wri U^filefunctemp 'end if'
wri U^filefunctemp 'if (^__suppress_orig_ver = "y")'
wri U^filefunctemp 'ver y'
wri U^filefunctemp 'else'
wri U^filefunctemp 'ver n'
wri U^filefunctemp 'end if'
clo U^filefunctemp
in "cvtempfunc94b5d143a12558bb414813edae566d2e"
lib
    del cvtempfunc94b5d143a12558bb414813edae566d2e.seq
go
```


## TODO

-   [ ] Documentation
-   [x] Function support
-   [ ] Helper for graphics
