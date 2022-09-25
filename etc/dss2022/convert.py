# this version of the 'convert' script for DSS 2022
# expects to concatenate a few columns in the input
# thereby reduce the number of columns in the output
# see create-nextview.sql

import csv
import sys
import re

concatenate_cols = [
    [0],
    [1],
    [2],
    [3, 4],
    [6],
    [8],
    [10, 20],         # person
    [11, 5, 15, 19],  # place
    [13, 14],         # maker = org + person
    [9, 21],          # org
    [25],
    [12],
    [15],
    [16],
    [17],
    [18],
    [22],
    [23],
    [24],
    [7]
]

txt_file = sys.argv[1]
csv_file = sys.argv[2]

with open(txt_file, "r") as in_text:
    in_reader = csv.reader(in_text, delimiter='\t')
    with open(csv_file, "w") as out_csv:
        out_writer = csv.writer(out_csv, escapechar='\\', quoting=csv.QUOTE_NONE, delimiter='\t')
        for row in in_reader:
            output_row = []
            for cols in concatenate_cols:
                output_row.append('|'.join([row[c] for c in cols if row[c] != '']))
            out_writer.writerow(output_row)
