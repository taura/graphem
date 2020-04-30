import sqlite3,sys,os,types,math,traceback,re,time

_dbg=0

def _Es(s):
    sys.stderr.write(s)

class graph_attributes:
    def __init__(self, kw, sg):
        K = kw.copy()
        self.plot        = K.pop("plot",        sg.default_plot)
        self.terminal    = K.pop("terminal",    sg.default_terminal)
        self.output      = K.pop("output",      sg.default_output)
        self.graph_title = K.pop("graph_title", sg.default_graph_title)
        self.xrange      = K.pop("xrange",      sg.default_xrange)
        self.yrange      = K.pop("yrange",      sg.default_yrange)
        self.xlabel      = K.pop("xlabel",      sg.default_xlabel)
        self.ylabel      = K.pop("ylabel",      sg.default_ylabel)
        self.boxwidth    = K.pop("boxwidth",    sg.default_boxwidth)
        self.graph_attr  = K.pop("graph_attr",  sg.default_graph_attr)
        self.pause       = K.pop("pause",       sg.default_pause)
        self.gpl_file    = K.pop("gpl_file",    sg.default_gpl_file)
        self.save_gpl    = K.pop("save_gpl",    sg.default_save_gpl)
        self.graph_variable_order = K.pop("graph_variable_order", [])
        to_delete = []
        for k,vals in K.items():
            if not isinstance(vals, type([])):
                _Es("warning: the value you supplied for graph parameter '%s' is not a list (%s). "
                   "the parameter '%s' ignored.\n" % (k, vals, k))
                to_delete.append(k)
        for k in to_delete:
            del K[k]
        for k in self.graph_variable_order:
            if k not in K:
                _Es("warning: the variable you supplied in graph_variable_order (%s) does not "
                    "appear in the keyword parameters (%s), ignored\n" % (k, K.keys()))
                self.graph_variable_order.remove(k)
        self.variables = K

    def _is_string(self, x):
        # if type(x) is types.StringType or type(x) is types.UnicodeType:
        if isinstance(x, type("")):
            return 1
        else:
            return 0

    def _is_critical(self, k):
        if k == "gpl_file":
            return 1
        else:
            return 0

    def _safe_instantiate(self, k, v, binding):
        try:
            # return v % binding
            return v.format(**binding)
        except Exception:
            e = sys.exc_info()
            _Es("warning: instantiating template '%s' for %s with bindings = %s "
                "caused an exception (%s)\n" 
                % (v, k, binding, e[1].args))
            traceback.print_exc()
            if self._is_critical(k):
                return None
            else:
                return v

    def _safe_apply(self, k, f, binding):
        return f(binding)
        try:
            return f(binding)
        except Exception:
            e = sys.exc_info()
            _Es("warning: applying callable %s (for %s) "
                "raised an exception %s (bindings = %s)\n" 
                % (f, k, e[1].args, binding))
            traceback.print_exc()
            if self._is_critical(k):
                return None
            else:
                return v
        
    def _instantiate(self, binding, sg):
        D = {}
        for k,v in self.__dict__.items():
            if k == "variables":
                pass
            else:
                if callable(v):
                    new_v = self._safe_apply(k, v, binding)
                elif self._is_string(v):
                    new_v = self._safe_instantiate(k, v, binding)
                else:
                    new_v = v
                if new_v is None: return None
                D[k] = new_v
        for k,v in self.variables.items():
            D[k] = v
        return graph_attributes(D, sg)

    def _canonicalize(self, sg):
        if self.terminal is None: 
            self.terminal = sg.default_terminal

    def _get_terminal_type(self):
        """
        terminal : string : specifies thee full gnuplot terminal string,
         such as "epslatex size 10cm,5cm"

        extract the 'type' from the terminal spec ("epslatex" from
        "epslatex size 10cm,5cm"
        """
        f = self.terminal.split()
        if len(f) == 0:
            return ""
        else:
            return f[0].lower()

    def _is_epslatex(self):
        if self._get_terminal_type() == "epslatex":
            return 1
        else:
            return 0

    def _is_display(self):
        t = self._get_terminal_type()
        if t == "" or t == "wxt" or t == "x11" or t == "xterm":
            return 1
        else:
            return 0

    def _show(self, indent):
        for k,v in self.__dict__.items():
            if k != "variables":
                _Es(" " * indent)
                _Es("%s : %s\n" % (k, v))


class plots_spec:
    def __init__(self, expr, kw, sg):
        K = kw.copy()
        self.expr           = expr
        self.plot_title     = K.pop("plot_title", sg.default_plot_title)
        self.plot_with      = K.pop("plot_with",  sg.default_plot_with)
        self.using          = K.pop("using",      sg.default_using)
        self.plot_attr      = K.pop("plot_attr",  sg.default_plot_attr)
        self.symbolic_x     = K.pop("symbolic_x", sg.default_symbolic_x)
        self.verbose_sql    = K.pop("verbose_sql", sg.default_verbose_sql)
        self.plot_variable_order = K.pop("plot_variable_order", [])
        to_delete = []
        for k,vals in K.items():
            if not isinstance(vals, type([])):
                _Es("warning: the value you supplied for plot parameter '%s' is not a list (%s). "
                   "the parameter '%s' ignored.\n" % (k, vals, k))
                to_delete.append(k)
        for k in to_delete:
            del K[k]
        for k in self.plot_variable_order:
            if k not in K:
                _Es("warning: the variable you supplied in plot_variable_order (%s) does not "
                    "appear in the keyword parameters (%s), ignored\n" % (k, K.keys()))
                self.plot_variable_order.remove(k)
        self.variables = K

    def _is_string(self, x):
        # if type(x) is types.StringType or type(x) is types.UnicodeType:
        if isinstance(x, type("")):
            return 1
        else:
            return 0

    def _is_critical(self, k):
        if k == "expr":
            return 1
        else:
            return 0

    def _safe_instantiate(self, k, v, binding):
        try:
            # return v % binding
            return v.format(**binding)
        except Exception:
            e = sys.exc_info()
            _Es("warning: instantiating template '%s' for %s with bindings = %s "
                "caused an exception (%s)\n" 
                % (v, k, binding, e[1].args))
            traceback.print_exc()
            if self._is_critical(k):
                return None
            else:
                return v

    def _safe_apply(self, k, f, binding):
        # return f(binding)
        try:
            return f(binding)
        except Exception:
            e = sys.exc_info()
            _Es("warning: applying callable %s (for %s) "
                "raised an exception %s (bindings = %s)\n" 
                % (f, k, e[1].args, binding))
            traceback.print_exc()
            if self._is_critical(k):
                return None
            else:
                return f
        
    def _expand_sql(self, sql, verbose, sg):
        db,query = sql[0],sql[1]
        init_s = ""
        init_f = ""
        funcs = []
        aggrs = []
        colls = []
        if len(sql) > 2: init_s = sql[2]
        if len(sql) > 3: init_f = sql[3]
        if len(sql) > 4: funcs = sql[4]
        if len(sql) > 5: aggrs = sql[5]
        if len(sql) > 6: colls = sql[6]
        if verbose>=2:
            _Es(r"""==== sql ====
 db: %s
 query: %s
 init_s: %s
 init_f: %s
""" % (db, query, init_s, init_f))
        if verbose>=1:
            t0 = time.time()
            _Es("sql begin ...\n")
        e = sg._do_sql_noex(db, query, init_s, init_f, 
                            funcs, aggrs, colls, 0, 0, verbose)
        if verbose>=1:
            t1 = time.time()
            _Es("... took %f sec\n" % (t1 - t0))
        if e is None:
            _Es(" error occurred during sql query:\n")
        elif len(e) == 0:
            _Es("warning: the following query has no data\n************\n%s\n************\n" % query)
        if verbose>=2:
            _Es(" result:\n")
            for t in e:
                for i,x in enumerate(t):
                    _Es(" %s" % x)
                _Es("\n")
            _Es("==== sql end ====\n")
        return e

    def _instantiate(self, binding, graph_binding, sg):
        """
        instantiate plot
        """
        if _dbg>=3:
            _Es('    plots_spec.instantiate(binding=%s, graph_binding=%s)\n'
               % (binding, graph_binding))
        all_binding = binding.copy()
        all_binding.update(graph_binding)
        D = {}
        for k,v in self.__dict__.items():
            if k == "variables" or k == "expr":
                # the reason we exclude symbolic_x here and
                # do not exclude other predefined keywords is ugly.
                # symbolic_x may be callable, so if treated below,
                # we might call it with the wrong number of args
                # we need to implement similar things for other
                # keywords that might cause trouble when treated below
                pass
            else:
                if callable(v):
                    new_v = self._safe_apply(k, v, all_binding)
                    if new_v is None: return None
                elif self._is_string(v):
                    if _dbg>=4:
                        _Es('     template = %s\n' % v)
                    new_v = self._safe_instantiate(k, v, all_binding)
                    if new_v is None: return None
                else:
                    new_v = v
                D[k] = new_v
        for k,v in self.variables.items():
            D[k] = v
        if callable(self.expr):
            e = self._safe_apply("expr", self.expr, all_binding)
            if e is None: return None
            return plots_spec(e, D, sg)
        elif self._is_string(self.expr):
            e = self._safe_instantiate("expr", self.expr, all_binding)
            if e is None: return None
            return plots_spec(e, D, sg)
        elif isinstance(self.expr, type((1,2,3))):
            # sql query
            i = lambda x: self._safe_instantiate("expr", x, all_binding)
            if isinstance(self.expr[0], sqlite3.Connection):
                sql = (self.expr[0],) + tuple(map(i, self.expr[1:4])) + self.expr[4:]
            else:
                sql = tuple(map(i, self.expr[:4])) + self.expr[4:]
            if sql[0] is None or sql[1] is None: return None
            e = self._expand_sql(sql, self.verbose_sql, sg)
            if e is None: return None
            return plots_spec(e, D, sg)
        else:
            return plots_spec(self.expr, D, sg)

    def _show(self, indent):
        for k,v in self.__dict__.items():
            if k != "variables":
                _Es(" " * indent)
                _Es("%s : %s\n" % (k, v))

class lots_plots:
    """
    smart_gnuplotter provides a higher level interface to gnuplot,
    making it particularly easy to generate many graphs of many
    plots with a single command.  A basic example is as follows:

    g = smart_gnuplotter()
    g.graphs('sin(x)')
    
    You will see the plot of sin(x) on display, just as you will
    when you type
       plot sin(x)
    to gnuplot.

    More interestingly, you can generate multiple plots by giving
    a parameterized expression and values for the pameters. For 
    example,

    g.graphs('sin(%(a)s * x)', a=[1,2,3])

    will show you three plots sin(1 * x), sin(2 * x), and sin(3 * x).
    It is as if you type 
       plot sin(1 * x),sin(2 * x),sin(3 * x)
    to gnuplot.  You may have multiple parameters, in which case
    all combinations are generated.

    Finally, you can generate multiple graphs by specifying some of
    parameters as "graph_vars". For example,

    g.graphs('sin(%(a)s * x + %(b)s * pi)', 
             a=[1,2], b=[0.0, 0.2], graph_vars=['a'])

    will generate two graphs, one for a=1 and the other for a=2.
    Each graph has two plots, one for b=0.0 and the other for 0.2

    You can give to the first argument either
    (1) python string (e.g., 'sin(x)', '"data.txt"', '"< cut -b 9-19 file.txt"'), 
    which are simply passed to gnuplot's plot command
    (2) python list, which are passed to gnuplot as in-place data (plot '-')
    (3) python tuple, which are treated as q query to sqlite3 database
    and the query results are passed to gnuplot as in-place data

    The last feature, combined with the parameterization, makes it 
    particularly powerful to show data in database from various angles
    and with various data selection criterion.

    You may overlay multiple different plots in the following step.
    g.set_graph_attrs()
    g.add_plots('sin(%(a)s * x)', a=[1,2])
    g.add_plots('%(b)s * x * x', b=[3,4])
    g.show_graphs()

    Essentially, g.graphs(expr) is a shortcut of the above

    g.set_graph_attrs()
    g.add_plots(expr)
    g.show_graphs()

    There are ways to specify whatever attributes you can specify with
    gnuplot.  Changing a terminal for all graphs takes a single line.
    See the explanation of the following methods for details.
    
    set_graph_attrs()
    add_plots()

    """
    def __init__(self):
        self.default_plot = "plot"
        self.default_terminal = ""
        self.default_output = ""
        self.default_graph_title = ""
        self.default_xrange = ""
        self.default_yrange = ""
        self.default_xlabel = ""
        self.default_ylabel = ""
        self.default_boxwidth = ""
        self.default_graph_attr = ""
        self.default_pause = -1
        self.default_gpl_file = ""
        self.default_save_gpl = 0
        # plot attributes
        self.default_plot_title = None
        self.default_plot_with = ""
        self.default_using = ""
        self.default_symbolic_x = 0
        self.default_verbose_sql = 0
        self.default_plot_attr = ""
        # 
        self.default_overlays = []
        # specify which ones in variables are graph variables
        self.default_graph_vars = []
        # 
        self.default_functions = []
        self.default_aggregates = [ ("cimin", 2, cimin), ("cimax", 2, cimax), ("ciavg", 2, ciavg) ]
        self.default_collations = []
        self.gpl_file_counter = 0
        self.all_graphs = []
        self.quit = 0

    def _is_string(self, x):
        # if type(x) is types.StringType or type(x) is types.UnicodeType:
        if isinstance(x, type("")):
            return 1
        else:
            return 0

    def _show_kw(self, kw, indent):
        for k,v in kw.items():
            if k != "variables":
                _Es(" " * indent)
                _Es("%s : %s\n" % (k, v))

    def _run_gnuplot(self, filename):
        """
        run gnuplot filename
        and return the status
        """
        cmd = "gnuplot %s" % filename
        if _dbg>=1: _Es("%s\n" % cmd)
        return os.system(cmd)

    def _safe_int(self, line):
        try:
            return int(line)
        except ValueError:
            return None

    def _expand_vars_rec(self, K, V, A, O):
        """
        K : a dictionary containing variables to expand
        V : a dictionary containing variables that have been bound
        A : a list to accumulate all bindings
        O : list of variables to specify which varialbe to expand first
        """
        if len(K) == 0:
            A.append(V.copy())
        else:
            if len(O) > 0:
                k = O.pop(0)
                vals = K.pop(k)
            else:
                k,vals = K.popitem()
            assert (isinstance(vals, type([]))), (k, vals)
            for v in vals:
                assert (k not in V), (k, V)
                V[k] = v
                self._expand_vars_rec(K, V, A, O)
                del V[k]
            K[k] = vals
        return A

    def _expand_vars(self, K, O):
        """
        e.g., 
        expand_vars({ "a" : [1,2], "b" : [3,4] })

        ==> [ { "a" : 1, "b" : 3 },
              { "a" : 1, "b" : 4 },
              { "a" : 2, "b" : 3 },
              { "a" : 2, "b" : 4 } ]

        """
        if _dbg>=3:
            _Es('    expand_vars(vars=%s)\n' % K)
        R = []
        for D in self._expand_vars_rec(K, {}, [], O):
            E = D.copy()
            for k,v in D.items():
                # when the value is a tuple (e.g., "x" : (3, 4)),
                # register "x[0]" : 3 and "x[1]" : 4 as well
                if 0:
                    if isinstance(v, type((1,2,3))):
                        for i in range(len(v)):
                            ki = "%s[%d]" % (k, i)
                            vi = v[i]
                            if _dbg>=3:
                                _Es('     adding binding %s <- %s\n' % (ki, vi))
                            E[ki] = vi
                else:
                    if isinstance(v, type((1,2,3))):
                        for i,ki in enumerate(k.split("__", len(v)-1)):
                            vi = v[i]
                            if _dbg>=3:
                                _Es('     adding binding %s <- %s\n' % (ki, vi))
                            E[ki] = vi
            R.append(E)
        return R


    def _expand_plots(self, graph_binding):
        if _dbg>=3:
            _Es('   expand_plots(graph_binding=%s)\n' % graph_binding)
        plots = []
        for p in self.plots:
            bindings = self._expand_vars(p.variables, p.plot_variable_order)
            if _dbg>=3:
                _Es('    -> bindings = %s\n' % bindings)
            for binding in bindings:
                q = p._instantiate(binding, graph_binding, self)
                if q is None: return None
                if _dbg>=3:
                    _Es('    -->\n')
                    q._show(5)
                plots.append(q)
        return plots

    def _x_is_symbol(self, data):
        for row in data:
            try:
                float(row[0])
            except:
                return 1
        return 0

    def _write_plots_tics(self, wp, plots):
        T = {}                  # symbol -> position
        for ps in plots:
            if isinstance(ps.expr, type([])):
                if ps.symbolic_x: #  or self._x_is_symbol(ps.expr)
                    # assign each row a unique number
                    for row in ps.expr:
                        # row is a single record. for example, 
                        # if the query is select a,b,c,x, row
                        # is a four tuple. we extract all colums
                        # except the last and use it as a symbol
                        # displayed in the x-axis
                        x = row[:-1]
                        if x not in T:
                            T[x] = len(T)
        if len(T) > 0:
            A = []
            for x,v in T.items():
                if callable(ps.symbolic_x):
                    # e.g., symbolic_x = lambda x,y,z: "x=%s y=%s z=%" 
                    s = ps.symbolic_x(*x)
                elif self._is_string(ps.symbolic_x):
                    # e.g., symbolic_x = "x=%s y=%s z=%" 
                    s = ps.symbolic_x % x
                else:
                    # e.g., symbolic_x = 1
                    s = " ".join(map(str, x))
                A.append('"%s" %d' % (s, v))
            wp.write('set xtics (%s)\n' % ", ".join(A))
            return T
        else:
            return None

    def _write_plots_exprs(self, wp, ga, plots):
        E = []
        if _dbg>=1:
            _Es('  %d plots\n' % len(plots))
        for ps in plots:
            e = []
            assert (not isinstance(ps.expr, type((1,2,3)))), ps.expr
            if isinstance(ps.expr, type([])) or isinstance(ps.expr, type((1,2,3))):
                if len(ps.expr) == 0:
                    continue
                else:
                    # python list or query
                    e.append("'-'")
            else:
                e.append(ps.expr)
            if ps.using != "": e.append("using %s" % ps.using)
            if ps.plot_with != "": e.append('with %s' % ps.plot_with)
            if ps.plot_title is not None: e.append('title "%s"' % ps.plot_title)
            e.append('%s' % ps.plot_attr)
            E.append(" ".join(e))
        if len(E) == 0:
            _Es("warning: plots %s have no data (skipped)\n" % plots)
        else:
            wp.write("%s %s\n" % (ga.plot, ", ".join(E)))
        return len(E)

    def _write_plots_data(self, wp, plots, tics):
        """
        tics : a dictionary mapping symbol -> numeric value
        """
        for ps in plots:
            if isinstance(ps.expr, type([])):
                if len(ps.expr) == 0:
                    continue
                elif tics is None:
                    for row in ps.expr:
                        wp.write("%s\n" % " ".join(map(str, row)))
                else:
                    # x is symbolic. convert the first row into a unique number
                    for row in ps.expr:
                        # e.g., given tics = { ..., ("cilk",0) -> 3 ... },
                        # convert ("cilk", 0, 15.3) --> (3, 15.3)
                        row = (tics[row[:-1]], row[-1])
                        wp.write("%s\n" % " ".join(map(str, row)))
                wp.write("e\n")

    def _write_pause(self, wp, ga):
        if ga._is_display():
            wp.write("pause %d\n" % ga.pause)

    def _tmp_gpl_file(self):
        f = "tmp_%d.gpl" % self.gpl_file_counter
        self.gpl_file_counter = self.gpl_file_counter + 1
        return f

    def _open_gpl(self, ga):
        gpl_file = ga.gpl_file
        if gpl_file == "": gpl_file = self._tmp_gpl_file()
        if _dbg>=3:
            _Es('   open gpl_file %s\n' % gpl_file)
        wp = open(gpl_file, "w")
        return gpl_file,wp

    def _cleanup_gpl(self, ga, gpl_file):
        if ga.save_gpl == 0:
            if _dbg>=1:
                _Es("remove %s\n" % gpl_file)
            os.remove(gpl_file)

    def _ext_name(self, output, ga):
        t = ga._get_terminal_type()
        ext_D = {
            "epslatex" : ".tex",
            "latex"    : ".tex",
            "fig"     : ".tex",
            "texdraw" : ".tex",
            "pslatex" : ".tex",
            "pstex"   : ".tex",
            "postscript" : ".eps",
            "jpeg"    : ".jpg",
            "svg"     : ".svg",
            "gif"     : ".gif",
            "png"     : ".png", }
        return output + ext_D.get(t, "")

    def _fix_include_graphics(self, tex):
        """
        tex : string : filename output by epslatex
        fix the \includegraphics{file} line of the tex file
        to \includegraphics{file.eps}.  this is necessary
        to make it possible to load this file with dvipdfm
        driver
        """
        tex2 = "%s.tmp" % tex
        fp = open(tex, "rb")
        x = fp.read()
        fp.close()
        y = re.sub("includegraphics\{([^\}]+)\}", 
                   r"includegraphics{\1.eps}", x)
        wp = open(tex2, "wb")
        wp.write(y)
        wp.close()
        os.rename(tex2, tex)

    def _write_graph_attr(self, wp, ga):
        if ga.terminal != "":
            wp.write('set terminal %s\n' % ga.terminal)
        if ga.output != "":
            wp.write('set output "%s"\n'   % self._ext_name(ga.output, ga))
        if ga.graph_title is not None:
            wp.write('set title "%s"\n'    % ga.graph_title)
        if ga.xrange != "":
            wp.write('set xrange %s\n'   % ga.xrange)
        if ga.yrange != "":
            wp.write('set yrange %s\n'   % ga.yrange)
        if ga.xlabel != "":
            wp.write('set xlabel "%s"\n'   % ga.xlabel)
        if ga.ylabel != "":
            wp.write('set ylabel "%s"\n'   % ga.ylabel)
        if ga.boxwidth != "":
            wp.write('set boxwidth %s\n'   % ga.boxwidth)
        if ga.graph_attr != "":
            wp.write('%s\n'                % ga.graph_attr)

    def _open_sql(self, database, init_statements, init_file, 
                  functions, aggregates, collations, verbose):
        """
        database    : string : filename of an sqlite3 database 
        init_statements : string : sql statement(s) to run
        init_file   : string : filename containing sql statement(s)
        functions   : list of (name, arity, function) specifying
                      user defined functions. they are passed as
                      create_function(name, arity, function)
        aggregates  : list of (name, arity, function) specifying
                      user defined aggregates. they are passed as
                      create_aggregate(name, arity, function)
        collations  : list of (name, function) specifying
                      user defined collations. they are passed as
                      create_collation(name, function)
        connect to sqlite3 database database, 
        add user defined functions/aggregates/callations, 
        run init_statements and init_file,
        and return the connection object
        """
        if isinstance(database, sqlite3.Connection):
            co = database
        else:
            if verbose>=1:
                _Es("open sql connection\n")
            co = sqlite3.connect(database)
        if functions is None: 
            functions = self.default_functions
        else:
            functions = self.default_functions + functions 
        if aggregates is None: 
            aggregates = self.default_aggregates
        else:
            aggregates = self.default_aggregates + aggregates 
        if collations is None: 
            collations = self.default_collations
        else:
            collations = self.default_collations + collations 
        for name,arity,f in functions:
            co.create_function(name, arity, f)
        for name,arity,f in aggregates:
            co.create_aggregate(name, arity, f)
        for name,f in collations:
            co.create_aggregate(name, f)
        if init_statements != "":
            co.executescript(init_statements)
        if init_file != "":
            fp = open(init_file, "rb")
            script = fp.read()
            fp.close()
            co.executescript(script)
        return co

    def open_sql(self, database, init_statements="", init_file="", 
                 functions=None, aggregates=None, collations=None, verbose=0):
        if functions is None:  functions = []
        if aggregates is None: aggregates = []
        if collations is None: collations = []
        return self._open_sql(database, init_statements, init_file, 
                              functions, aggregates, collations, verbose)
    
    def _do_sql_ex(self, database, query, init_statements, init_file,
                   functions, aggregates, collations, 
                   single_row, single_col, verbose):
        if _dbg>=3:
            _Es("   do_sql_ex(database=%s,query=%s,init_statements=%s,init_file=%s,functions=%s,aggregates=%s,collations=%s,single_row=%s,single_col=%s, verbose=%s)\n" 
               % (database, query, init_statements, init_file, 
                  functions, aggregates, collations, single_row, single_col, verbose))
        co = self._open_sql(database, init_statements, init_file, 
                            functions, aggregates, collations, verbose)
        if single_row and single_col:
            for (result,) in co.execute(query):
                break
        elif single_row and single_col == 0:
            for result in co.execute(query):
                break
        elif single_row == 0 and single_col:
            result = []
            for (x,) in co.execute(query):
                result.append(x)
        else:
            assert(single_row == 0)
            assert(single_col == 0)
            result = []
            for x in co.execute(query):
                result.append(x)
        if co is not database:
            co.close()
        return result

    def _do_sql_noex(self, database, query, init_statements, init_file,
                     functions, aggregates, collations, 
                     single_row, single_col, verbose):
        try:
            return self._do_sql_ex(database, query, init_statements, init_file,
                                   functions, aggregates, collations, 
                                   single_row, single_col, verbose)
        except sqlite3.OperationalError:
            e = sys.exc_info()
            _Es("error during sql query %s\n" % (e[1].args,))
            return None

    def do_sql(self, database, query, init_statements="", init_file="",
               functions=[], aggregates=[], collations=[], 
               single_row=0, single_col=0, verbose=0):
        """
        database    : string : filename of an sqlite3 database 
        init_statements : string : sql statement(s) to run
        init_file   : string : filename containing sql statement(s)
        functions   : list of (name, arity, function) specifying
                      user defined functions. they are passed as
                      create_function(name, arity, function)
        aggregates  : list of (name, arity, function) specifying
                      user defined aggregates. they are passed as
                      create_aggregate(name, arity, function)
        collations  : list of (name, function) specifying
                      user defined collations. they are passed as
                      create_collation(name, function)
        connect to sqlite3 database database, 
        add user defined functions/aggregates/callations, 
        run init_statements and init_file,
        execute the query,
        and return the result.

        when single_row == 0 and single_col == 0:
          it is returned as a list of tuples
        when single_row == 1,
          it is assumed that the result has only a single row,
          and that row is returned
        when single_col == 1,
          it is assumed that each row has a single column
          and each element of the list becomes that column
          instead of a singleton tuple.
        """
        return self._do_sql_noex(database, query, init_statements, init_file,
                                 functions, aggregates, collations, 
                                 single_row, single_col, verbose)

    def _prompt(self, ga):
        _Es("[s/q/<num>/other]? ")
        line = sys.stdin.readline().strip()
        _Es("\n")
        if line[0:1] == "s":
            ga.pause = self.graph_attr.pause = self.default_pause = 0
        elif line[0:1] == "q":
            _Es("quit\n")
            self.quit = 1
        else:
            x = self._safe_int(line)
            if x is not None:
                ga.pause = self.graph_attr.pause = self.default_pause = x
            else:
                # _Es("you hit [%s]\n" % line)
                pass
        return self.quit

    def _show_graph(self, ga, graph_binding):
        if _dbg>=3:
            _Es('  show_graph(graph_binding=%s)\n' % graph_binding)
        gpl_file,wp = self._open_gpl(ga)
        self._write_graph_attr(wp, ga)
        plots = self._expand_plots(graph_binding)
        if plots is None: return 1 # NG
        # set xtics ...
        tics = self._write_plots_tics(wp, plots)
        # plot expr with ..., expr with ..., ...
        r = 0
        if self._write_plots_exprs(wp, ga, plots) > 0:
            self._write_plots_data(wp, plots, tics)
            self._write_pause(wp, ga)
            wp.close()
            r = self._run_gnuplot(gpl_file)
            self.all_graphs.append(ga)
            if ga._is_epslatex():
                output = self._ext_name(ga.output, ga)
                # self._fix_include_graphics(output)
            if ga._is_display() and ga.pause < 0:
                self._prompt(ga)
        if r:
            _Es("there was an error in gnuplot, file '%s' "
                "left for your inspection\n" % gpl_file)
        else:
            self._cleanup_gpl(ga, gpl_file)
        return r

    def _separate_variables(self, kw, graph_vars):
        if _dbg>=3:
            _Es(' separate_variables(graph_vars=%s)' % graph_vars)
            _Es(' kw:\n')
            self._show_kw(kw, 2)
        plot_variables = kw.copy()
        graph_variables = {}
        ga = graph_attributes({}, self)
        for k in ga.__dict__.keys():
            if k in plot_variables:
                graph_variables[k] = plot_variables.pop(k)
        for k in graph_vars:
            if k in plot_variables:
                graph_variables[k] = plot_variables.pop(k)
        return graph_variables,plot_variables

    def set_graph_attrs(self, **kw):
        """
        This method sets the attribute of the graphs that will
        be drawn by the next call to show_graphs().  For example,

        g = smart_gnuplotter()
        g.set_graph_attrs(graph_title="my graph", xrange="[-2:2]")
        g.add_plots(...)
        g.show_graphs()

        will generate a graph whose title is "my graph" and xrange
        is [-2:2].  As you might have imagined, most attributes are
        simply translated into a corresponding gnuplot 'set' command.

        These attributes may be parameterized; in other words, they 
        may contain placeholders such as %(a)s, %(b)s, etc., in which
        case you also need to supply possible values for them.
        The following is a valid parameterization.

        g.set_graph_attrs(graph_title="graph (a=%(a)s)", a=[1,2,3])

        This will generate three graphs (one for a=1, another for a=2,
        and the other for a=3).  The title of each of the three graphs
        will be "graph (a=1)", "graph (a=2)", and "graph (a=3)",
        respectively.

        The following is the attributes direcly supported by keyword
        arguments and their meanings. Most of them have obvious 
        counterpart in gnuplot's 'set' command

        terminal    : terminal specification
                      (e.g., "png", "postscript", "epslatex color size 10cm,4cm")
        output      : output filename
        graph_title : title of the graph
        xrange      : xrange of the graph
        yrange      : yrange of the graph
        xlabel      : xlabel of the graph
        ylabel      : ylabel of the graph
        boxwidth    : boxwidth, meaningful only when you use boxes style for plots
        pause       : pause after you show a graph on display. meaningful only when
                      the terminal is a display ("wxt", "x11", or "xterm")
        plot        : either "plot" or "splot", depending on you perfom 2d plot or
                      3d plot
        save_gpl    : 0 or 1. if 1, a temporary file to which gnuplot commands are
                      written will not be deleted. useful for diagnosis.
        gpl_file    : name of the temporary filename to which gnuplot commands are
                      written. if specified, it implies save_gpl=1

        To set other attributes supported by gnuplot, you may use parameter 
        'graph_attr'
                      
        graph_attr  : any string that is given to gnuplot before the plot command
                      is issued. you may write any valid gnuplot command.

        Automatic extension of the output: for typical terminal types,
        the filename you give to the output parameter is automatically
        extended with a proper extension.  For example, if you say output="foo"
        and terminal="postscript", you actually get foo.eps.
        It is particularly convenient when you switch from one terminal 
        to another; you normally do not have to change output parameter.
        Currently, the following is the list of terminal types and their
        associated extensions (I may have gotten some of them wrong; corrections
        are welcome).

            epslatex : .tex
            latex    : .tex
            fig      : .tex
            texdraw  : .tex
            pslatex  : .tex
            pstex    : .tex
            postscript : .eps
            jpeg     : .jpg
            svg      : .svg
            gif      : .gif
            png      : .png

        """
        if _dbg>=3:
            _Es(' set_graph_attrs\n')
            self._show_kw(kw, 2)
        if self.quit: 
            _Es(' quit (self.quit == 1)\n')
            return self.quit
        self.graph_attr = graph_attributes(kw, self)
        self.plots = []

    def add_plots(self, expr, **kw):
        """
        expr : an expression to plot.  see below for accepted values

        This method lets expr to be drawn in each of the graphs 
        generated when you call show_graphs() next time.  For example,

        g = smart_gnuplotter()
        g.set_graph_attrs()
        g.add_plots("sin(x)")
        g.show_graphs()

        will plot sin(x).

        You may set various attributes of the plot.  For example,

        g.add_plots("sin(x)", plot_title="sin")

        will set the title of the plot to "sin".

        Expression, as well as the attributes, may be parameterized
        (may contain placeholders such as %(a)s, %(param)s, and so on),
        in which case you need to supply the values of these parameters.

        For example,

        g.add_plots("sin(%(a)s * x)", plot_title="sin(%(a)sx)",
                    a=[1,2,3])

        will plot sin(1*x), sin(2*x), and sin(3*x) in a single graph
        when you call show_graphs() next time.  The title of each of
        them will be sin(1x), sin(2x), and sin(3x), respectively.

        The following is the attributes direcly supported by keyword
        arguments and their meanings. 

        plot_title : title of the plot
        using      : columns to plot in datafile. you may give
                     any string you may specify after 'using'
                     in a plot.
        plot_with  : plot style. you may give any string you may 
                     specify after the 'with' in a plot.

        Besides, you may specify any string you may specify to modify
        your plot by 'plot_attr' parameter.

        plot_attr  : any string you may specify for a plot.

        Possible values for expr parameter:

        (1) a python string : this is simply passed to gnuplot's plot
        command.  Gnuplot regularly interprets it as either an expression 
        (e.g., sin(x)), a datafile (e.g., "data.txt"), or a command by gnuplot 
        (e.g., "> grep ....").

        (2) a python list of tuples : this is passed to gnuplot's plot
        command as in-place data.  For example, if you give a list
        [ (1,2), (3,4) ], then it will be translated into:

             plot '-'
             1 2 
             3 4
             e

        (3) a python tuple : this is interpreted as a sqlite3 query.
        specifically, it is a tuple of
        (database, query, init_stataments, init_file, functions, aggregates, collations),
        where everything other than database and query are optional.

        smart_gnuplotter connects to database, add user-defined
        functions/aggregates/collations as specified, execute SQL
        statements init_statements and those in init_file, and finally
        issue the query.  The result is extracted as a list of tuples
        and the rest of the process is the same as (2).

        An example: 
        g.add_plots(("a.sqlite", "select a,b from T"))
        g.add_plots(("a.sqlite", 
                     "select a,b from J", "create temp table J as select * from T natural join S"))
        g.add_plots(("a.sqlite", 
                     "select a,b from J", "create temp table J as select * from T natural join S",
                     "init.sql"))
        g.add_plots(("a.sqlite", 
                     "select a,b from J", "create temp table J as select * from T natural join S",
                     "init.sql"))

        functions, aggregates, and collations are lists.  
        - Each element of functions is a triple (name, arity, python_function)
        which is translated into a call create_function(name, arity, python_function)
        on the sqlite3 connection object.
        - Each element of aggregates is a triple (name, arity, python_class)
        which is translated into a call create_aggregate(name, arity, python_class)
        - Each element of collations is a pair (name, python_function)
        which is translated into a call create_collation(name, python_function).
        see the documentation of python sqltie3 module.

        """
        if _dbg>=3:
            _Es(' add_plots("%s")\n' % str(expr))
            self._show_kw(kw, 2)
        if self.quit: 
            _Es(' quit (self.quit == 1)\n')
            return self.quit
        self.plots.append(plots_spec(expr, kw, self))

    def show_graphs(self):
        """
        show in display or generate files of the graphs, specified by
        prior calls to set_graph_attrs and add_plots.
        """
        if _dbg>=3:
            _Es(' show_graphs()\n')
        if self.quit: 
            _Es(' quit (self.quit == 1)\n')
            return self.quit
        graph_bindings = self._expand_vars(self.graph_attr.variables,
                                           self.graph_attr.graph_variable_order)
        self.graph_attr._canonicalize(self)
        if _dbg>=1:
            _Es(' %d graphs\n' % len(graph_bindings))
        for graph_binding in graph_bindings:
            ga = self.graph_attr._instantiate(graph_binding, self)
            if ga is None: return 1 # NG
            r = self._show_graph(ga, graph_binding)
            if r: 
                _Es("abort\n")
                return r
            if self.quit: 
                _Es("quit\n")
                sys.exit(1)
                return r
        return 0

    def graphs(self, expr, graph_vars=None, overlays=None, **kw):
        """
        show graphs, with specified graph attributes as well
        as plot attributes.  In summary, 

          g.graphs(expr, ...)
  
        is a shortcut for:

          g.set_graph_attr(...)
          g.add_plots(expr, ...)
          g.show_graphs()

        You may give to graphs all parameters accepted by
        set_graph_attrs or add_plots.  Parameters accepted by
        set_graph_attrs and paramters specified in the 'graph_vars'
        are given to set_graph_attr. Other parameters are given to
        add_plots.  See the documentation of the above two
        methods for details.

        overlays is a python list and gives a convenient way to put
        many plots that are difficult to parameterize with a single
        set of parameters.  For example, overlays=[("x", {})]
        puts a plot y=x in the same graph.

        Each element of the list is 
        (expression, dictionary)
        In the dictionary, you may specify any key-value pair
        you may give to add_plots.  For example,
        overlays=[("x", { "plot_title" : "ideal", "plot_with" : "lines" })]
        is equivalent to 
          add_plots("x", plot_title="ideal", plot_with="lines")
        In essence, each element is translated into a call
          add_plots(expression, **dictionary)
        overlays parameter is primarily meant to put a simple
        plot or two in a graph you want to show your data in.  
        To overlay multiple graphs of different kinds, the better
        practice will be to call set_graph_attrs(), make a series
        of calls to add_plots() and finally call show_graphs().
        
        """
        if graph_vars is None: graph_vars = []
        if overlays is None: overlays = []
        if _dbg>=3:
            _Es('graphs("%s", graph_vars=%s, overlays=%s)\n' 
               % (expr, graph_vars, overlays))
            self._show_kw(kw, 1)
        if self.quit: 
            _Es(' quit (self.quit == 1)\n')
            return self.quit
        g_variables,p_variables = self._separate_variables(kw, graph_vars)
        if "graph_variable_order" not in g_variables:
            g_variables["graph_variable_order"] = graph_vars
        if _dbg>=3:
            _Es(' graph_variables:\n')
            self._show_kw(g_variables, 2)
            _Es(' plot_variables:\n')
            self._show_kw(p_variables, 2)
        self.set_graph_attrs(**g_variables)
        self.add_plots(expr, **p_variables)
        for o_expr,o_opts in overlays:
            self.add_plots(o_expr, **o_opts)
        return self.show_graphs()

    def generate_tex_file(self, tex_file):
        wp = open(tex_file, "wb")
        wp.write(r"""
\documentclass[8pt,dvipdfmx]{article}
\setlength{\oddsidemargin}{-1.3truecm}
\setlength{\evensidemargin}{-1.3truecm}
\setlength{\textwidth}{18.5truecm}
\setlength{\headsep}{1truecm}
\setlength{\topmargin}{-2truecm}
\setlength{\textheight}{25truecm}
\usepackage{graphicx}
\begin{document}
""")
        for ga in self.all_graphs:
            if ga._is_epslatex():
                wp.write(r"""
%%\begin{figure}

\begin{verbatim}
%(filename)s
\end{verbatim}

\input{%(filename)s}


%%\end{figure}
""" % { "filename" : ga.output, "caption" : ga.output })
        wp.write(r"""
\end{document}
""")
        wp.close()

class confidence_interval:
    """
    this class is a base to extend sqlite3 with cimin/cimax aggregates
    """
    def _f(self, t, nu):
        A = math.gamma((nu + 1) * 0.5)
        B = math.sqrt(nu * math.pi) * math.gamma(nu * 0.5)
        C = math.pow(1 + t * t / nu, -(nu + 1) * 0.5)
        return (A * C) / B 

    def _rk_step(self, f, t, dt):
        k1 = f(t)
        k2 = f(t + dt * 0.5)
        k3 = f(t + dt * 0.5)
        k4 = f(t + dt)
        dy = dt / 6.0 * (k1 + 2.0*k2 + 2.0*k3 + k4)
        return dy

    def _find_x(self, f, a, dt, J):
        """
        return x s.t. int_a^x f(t)dt = J
        
        """
        # print "find_x(f, %f, %f, %f)" % (a, dt, J)
        t = a
        I = 0.0
        while 1:
            dI = self._rk_step(f, t, dt)
            if I + dI < J:
                I += dI
                t += dt
            elif dt < 1.0E-6:
                return t
            else:
                return self._find_x(f, t, dt * 0.1, J - I)

    def _t_table(self, freedom, significance_level):
        """
        freedom : int 
        significance_level : float : 0.05, 0.01, etc.

        find a such that 
        int_{-a}^a f(t, freedom) dt = 1 - significance_level
        """
        g = lambda t: self._f(t, freedom)
        return self._find_x(g, 0.0, 0.01, (1 - significance_level) * 0.5)

    def _confidence_interval(self, X, significance_level):
        """
        return (mu, dm) s.t.  m +/- dm is the confidence interval
        of the average of probability density from which X was drawn,
        with the specified significance level 
        """
        n = len(X)
        # empirical average
        mu = sum(X) / float(n)
        # unbiased variance
        U = math.sqrt(sum([ (x - mu) * (x - mu) for x in X ]) / float(n - 1))
        t = self._t_table(n - 1, significance_level)
        dm = t * U / math.sqrt(n)
        return (mu, dm)

    def __init__(self):
        self.X = []
        self.significance_level = 0.05

    def step(self, value, sl):
        self.significance_level = sl
        self.X.append(value)

    def finalize(self):
        try:
            return self._finalize_()
        except Exception:
            #sys.stderr.write("Exception %s\n" % (e.args,))
            traceback.print_exc()
            raise

def remove_outliner(X):
    return X
    n = len(X)
    Y = X[:]
    while len(Y) > 0.5 * n:
        try:
            s = sum(Y)
        except TypeError:
            print(Y)
            raise
        m = sum(Y) / float(len(Y))
        Z = [ y for y in Y if abs((y - m) / m) < 1.0 ]
        if len(Z) == len(Y):
            break
        Y = Z
    else:
        print("warning: too many outliers %s -> %s" % (X, Y))
    return Y
        
class cimax(confidence_interval):
    def _finalize_(self):
        X = remove_outliner(self.X)
        mu,dm = self._confidence_interval(X, self.significance_level)
        return mu + dm

class cimin(confidence_interval):
    def _finalize_(self):
        X = remove_outliner(self.X)
        mu,dm = self._confidence_interval(X, self.significance_level)
        return mu - dm

class ciavg(confidence_interval):
    def _finalize_(self):
        X = remove_outliner(self.X)
        mu,dm = self._confidence_interval(X, self.significance_level)
        return mu

def _main():
    g = smart_gnuplotter()
    # g.graphs("sin(x)")
    g.graphs("sin(%(a)s * x)", a=[1,2], save_gpl=1)


