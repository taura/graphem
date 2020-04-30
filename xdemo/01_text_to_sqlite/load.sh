#!/bin/bash

db=a.sqlite

#
# [optional] I will often delete/clear database beforehand
# the default behavior is to add data into table
#
rm -f ${db}
#

#
# real job.
# parse out/*.txt and make rows of i, j, k and x
#

# M = 100, N = 100, K = 100
# 0 : T = 4006633

./txt2sql ${db} --table a \
        -e 'M = (?P<M>\d+), N = (?P<N>\d+), K = (?P<K>\d+)' \
        -r '(?P<idx>\d+) : T = (?P<T>\d+)' \
        out/*.txt

#
# [optional] I will often prints some data to make sure things went correctly
#

sqlite3 ${db} 'select * from a limit 10'
