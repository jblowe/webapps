# this version of the 'convert' script for DSS 2022
# expects to concatenate a few columns in the input
# thereby reduce the number of columns in the output
# see create-nextview.sql

import csv
import sys
import re

# map columns in input (4solr file) to columns in output file
# concatenating a few as needed
concatenate_cols = [
    [2],
    [3],
    [5],
    [16, 17],
    [23],
    [28],
    [30, 46],         # person      6
    [31, 19, 36, 45], # place       7
    [34, 35],         # maker = org + person
    [29, 47],         # org         9
    [80],
    [32],
    [36],
    [37],
    [38],
    [44],
    [48],
    [56],             # 17
    [64],
    [27],             # 19
    [24],
    [86]
]

# this is how the input columns are mapped to output columns
"""
index internal  field
     1	     2	objectname_ss
     2	     3	objectnumber_s
     3	     5	dhname_ss
     4	    16	physicaldescription_s
     5	    17	contentdescription_s
     6	    19	fieldcollectionplace_s
     7	    23	ipaudit_s
     8	    27	moddate_dt
     9	    28	assocculturalcontext_ss
    10	    29	assocorganization_ss
    11	    30	assocperson_ss
    12	    31	assocplace_ss
    13	    32	material_ss
    14	    34	objectproductionorganization_ss
    15	    35	objectproductionperson_ss
    16	    36	objectproductionplace_ss
    17	    37	title_ss
    18	    38	technique_ss
    19	    44	contentconcepts_ss
    20	    45	contentplaces_ss
    21	    46	contentpersons_ss
    22	    47	contentorganizations_ss
    23	    48	exhibitionhistories_ss
    24	    56	dimensionsummary_s
    25	    64	creditline_s
    26	    80	objectproductiondate_ss
    27	    24	copyrightholder_s
    28	    86	referencenote_s

output
you can create this: head -1 netxview.csv | perl -pe 's/\t/\n/g' | nl -v 0

     0	objectname_ss
     1	objectnumber_s
     2	dhname_ss
     3	physicaldescription_s contentdescription_s
     4	ipaudit_s
     5	assocculturalcontext_ss
     6	assocperson_ss,contentpersons_ss
     7	assocplace_ss,fieldcollectionplace_s,objectproductionplace_ss,contentplaces_ss
     8	objectproductionorganization_ss,objectproductionperson_ss
     9	assocorganization_ss,contentorganizations_ss
    10	objectproductiondate_ss
    11	material_ss
    12	objectproductionplace_ss
    13	title_ss
    14	technique_ss
    15	contentconcepts_ss
    16	exhibitionhistories_ss
    17	dimensionsummary_s
    18	creditline_s
    19	moddate_dt
    20	fieldcollectionnote_s
    21	referencenote_s
"""

# list of single-valued fields in the output, used so we don't encapsulate them
single_valued = [1, 2, 3, 4, 10, 13, 17, 19, 20, 21]

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
                # truncate exhibition histories on semicolon
                if cols[0] == 22:
                    row[cols[0]] = row[cols[0]].split(';')[0]
                if i in single_valued:
                    output_row.append(' '.join([row[c] for c in cols if row[c] != '']))
                else:
                    encapsulate(row, cols)
                    output_row.append(','.join([row[c] for c in cols if row[c] != '']))
            out_writer.writerow(output_row)
