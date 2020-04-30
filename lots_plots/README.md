lots_plots
=====================


Introduction
=====================

* This is a small Python library to display or generate graphs using gnuplots.
* You can easily switch between interactive viewing (gnuplot's X11 terminal) and uninteractive file generation.
* In particular, it can draw lots of graphs each with lots of curves with a single function call.
* It is especially useful to draw lots of graphs with data in an sqlite3 database.

A minimum example
=====================

```
import lots_plots as lp
g = lp.lots_plots()
g.graphs(("a.sqlite",
         r"""select M*N*K,avg((T+0.0)/(M*N*K)) from a group by M,N,K"""))
```

* Import the library, instantiate a lot_plots object, and call a graph.
* The argument is a tuple of a database file and a query.
* By default, the query should generate rows each of which is a pair of an x value and a y value.
* They are given to gnuplot's plot command and displayed by the default terminal (often x11 terminal).


... I will continue writing below, but look at ../xdemo/02_make_graphs/ directory for now ...

Drawing many curves within a single graph
=====================

Drawing many graphs
=====================

Customizing graphs
=====================

Seeing what is passed to gnuplot
=====================

