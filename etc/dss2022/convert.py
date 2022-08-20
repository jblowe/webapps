# this version of the 'convert' script for DSS 2022
# expects to import array columns as postgres arrays.
# see create-nextview.sql

import csv
import sys
import re

columns = [8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 24, 25]
# [3,4,5,6,11,12,13,14,15,16,17,18,19,20,22,23,25]

def encapsulate(cell):
    lst = cell.split('|')
    lst = ["'" + re.sub(r"('\]\[\}\{)", "\\\1'", l) + "'" for l in lst]
    arr = '{ ' + ','.join(lst) + ' }'
    if arr == "{ '' }" : arr = ''
    return arr


txt_file = sys.argv[1]
csv_file = sys.argv[2]

with open(txt_file, "r") as in_text:
    in_reader = csv.reader(in_text, delimiter='\t')
    with open(csv_file, "w") as out_csv:
        out_writer = csv.writer(out_csv, escapechar='\\', quoting=csv.QUOTE_NONE, delimiter='\t')
        for row in in_reader:
            for i, cell in enumerate(row):
                if i in columns:
                    row[i] = encapsulate(cell)
            out_writer.writerow(row)

