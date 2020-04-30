# a2sql --- any-to-sqlite3 tool

txtsq --- txt-to--sql
------------------

```
usage:

  txt2sql db_file arg arg arg ...
```

Each arg is one of --exp REGEXP, --row REGEXP, --table TABLE, --file FILE, and --drop.

This program reads text file(s) and create a sqlite database according to specified regular expressions.  A simple example:

A text file exp.log contains the following.
```
./a.out 3 
running time: 32.4 sec
./a.out 6 
running time: 27.8 sec
```

This program can create a database like the following (among others).
```
-------------------
|file   |x|runtime|
|exp.log|3|32.4   |
|exp.log|6|27.8   |
-------------------
```

This is achieved by
```
  txt2sql a.sqlite --table a_out_runtime \
               --exp './a.out (?P<x>.*)' \
               --row 'running time: (.?<runtime>.*) sec' \
               --file exp.log
```

* --table specifies the table name.

* Each --exp REGEXP specifies a regular expression the command should pay attention to.  You can specify as many --exp options as you like. For each line that matches the expression, it extracts the part enclosed by parens (i.e., (?P<x>.*) in this example, and remembers the string as the specified name (i.e., 'x' in this case).  Each such name becomes a column name of the table. Note that the regular expression is Python's notation.  The effect of --exp is simply to 'remember' the current value of a variable you are interested in. In this example, the first line matches './a.out (?P<x>.*)', so  at this point, the system records the value of 'x' as '3'.

* --row REGEXP is similar to --exp, but in addition, it emits a single row that has specified column values.  In this example, the second line matches 'running time: (.?<runtime>.*) sec', so at this point a row of two columns, x and runtime, is generated, whose values are x=3 and runtime=32.4.  This repeats until the end of file.

This semantics is particularly useful to parse a text log having a hierarchical structure.  When you run benchmarks, you typically write a shell loop that looks like:

```
 for x in 1 2  do
   echo "---- x=${x} ----"
   for y in a b do
     echo "  ---- y=${x} ----"
     ./your_program ${x} ${y}
   done
 done
```

./your_program will produce results such as "running time: 12.3 sec". So the entire output will look like:

```
---- x=1 ----
  ---- y=a ----
    running time: 12.3 sec
  ---- y=b ----
    running time: 45.6 sec
---- x=2 ----
  ---- y=a ----
    running time: 78.9 sec
  ---- y=b ----
    running time: 99.9 sec
```

Assuming the above is writte in exp.log, the following command line suffices to create the database you want.

```
txt2sql a.db \
  --table result \
  --exp '---- x=(?P<x>.*) ----' \
  --exp '---- y=(?P<y>.*) ----' \
  --row 'running time: (?P<runtime>.*) sec' \
  --file exp.log
```

If dbfile does not exist, it will be created.  If the table specified by --table does not exist in the database, it will be created.  If the table already exists, found data will be added to the database.  If the schema does not match, an error is signaled.  If you like to recreate the table, add --drop right before the --table option.  So the following is typical.

```
txt2sql a.db \
  --drop --table result \
  --exp '---- x=(?P<x>.*) ----' \
  --exp '---- y=(?P<y>.*) ----' \
  --row 'running time: (?P<runtime>.*) sec' \
  --file exp.log
```

You may specify as many --file FILENAME options.  Actually, --file can be omitted.  So, you may convert many text logs into a single database file by something like

```
txt2sql a.db \
  --drop --table result \
  --exp '---- x=(?P<x>.*) ----' \
  --exp '---- y=(?P<y>.*) ----' \
  --row 'running time: (?P<runtime>.*) sec' \
  result_dir/*.txt
```

