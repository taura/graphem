# How to use this directory

This is a skeleton directory I use whenever I make a new tex document (or a beamer slides)

```
make
```

will

1. generate lots of epslatex graphs in out/tex/data/mm/ by running data/mm/graphs.py;
2. do lots of other things such as converting svg files into pdfs; and
3. compile a tex file into a pdf that include lots of graphs generate in (2).

The part 2. depends on various tools and may be relatively Linux-dependent.  Specifically, it depends on

* `inkscape` to convert svg files under svg/
* `convert` to convert png/gif/jpg files under img/
* `convert` to convert pdf files under pdf/
* `gnuplot` to convert gnuplot (.gpl) files under gpl/
* `dot` and `inkscape` to convert graphviz (.dot) files under dot/
* `unoconv` to convert odg files under odg/

You may simply delete files under respective directories to get rid of errors due to command not found

The purposes of this directory are to demonstrate
* how to make a tex file with lots of graphs using lots_plots.py
* how to make a tex file with lots of other include files easily (you simply add or edit graphics files and a single make will do everything)

All files to be included are generated under a out/ directory.
You can simply `rm -rf out/` to recompile all component files.

```
make clean
```

will delete usual latex intermediate files (e.g., dvi).

