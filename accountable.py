#!/usr/bin/python

import sqlite3 as lite
import sys

from acc_classes import *

# See if we got an argument
if len(sys.argv) == 1:

    # No argument. Create a database?
    filename = raw_input("Enter the name of your database (If it doesn't exist, it will be created.):")

    if filename == "":
        sys.exit()
    elif filename[-3:] != ".db":
        filename = filename + ".db"

else:

    # We have an argument.
    filename = sys.argv[1]

con = lite.connect(filename)
with con:
    con.row_factory = lite.Row
    cur = con.cursor()
    acc = Account(con)
    acc.main()

sys.exit()

