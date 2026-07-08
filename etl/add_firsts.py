import sys, csv

firsts = [
    "A94.108.1",
    "2023.15.1",
    "A65.104.2",
    "H96.1.3075",
    "2010.54.21837",
    "A67.21.6",
    "2001.47.110",
    "2003.139.59.2",
    "S86.24",
    "2010.54.6352",
    "2021.16.1",
    "2022.1.477",
    "2003.139.59.2",
    "A79.165",
    "A75.36",
    "2009.64.14",
]

delim = ","

types = {}
errors = 0

# NB: the output file must also be opened with newline='' -- csv.writer supplies
# its own line terminator, and letting Python's text-mode translation touch it
# too is what caused the doubled-newline bug the old pipeline patched with a
# separate perl 's/\r//g' pass (unsafe here, since it would also mangle a
# legitimately quoted, embedded-newline field).
with open(sys.argv[2], 'w', newline='') as f2:
    # force \n: csv.writer defaults to \r\n, which doesn't match psql --csv
    writer = csv.writer(f2, delimiter=delim, quoting=csv.QUOTE_MINIMAL, lineterminator='\n')
    with open(sys.argv[1], 'r', newline='') as f1:
        reader = csv.reader(f1, delimiter=delim, quoting=csv.QUOTE_MINIMAL)
        for lineno, row in enumerate(reader):
            if lineno == 0:
                object_number_column = row.index('objectnumber_s')
                row.append('first_s')
            else:
                if row[object_number_column] in firsts:
                    row.append('t')
                else:
                    row.append('f')
            writer.writerow(row)
