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

# list if single-valued fields in the output, used so we don't encapsulate them
single_valued = [0, 1, 2, 4, 17, 19]

txt_file = sys.argv[1]
csv_file = sys.argv[2]

def encapsulate(row, cols):
    # encapsulate items with commas in double quotes, double the double quotes
    for c in cols:
        t = row[c].split('|')
        z = []
        for x in t:
            if ',' in x:
                x = f'"{x}"'
            z.append(x)
        row[c] = ','.join(z)

with open(txt_file, "r") as in_text:
    in_reader = csv.reader(in_text, delimiter='\t')
    with open(csv_file, "w") as out_csv:
        out_writer = csv.writer(out_csv, escapechar='\\', quoting=csv.QUOTE_MINIMAL, quotechar='"', delimiter='\t')
        for row in in_reader:
            output_row = []
            for i, cols in enumerate(concatenate_cols):
                if i in single_valued:
                    output_row.append(row[cols[0]])
                else:
                    encapsulate(row, cols)
                    output_row.append(','.join([row[c] for c in cols if row[c] != '']))
            out_writer.writerow(output_row)
