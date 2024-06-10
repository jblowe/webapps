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
    "2000.1.600",
    "2021.16.1",
    "2022.1.477",
    "H95.18.1189",
    "A79.165",
    "A69.68",
    "2009.64.14",
]

delim = "\t"

types = {}
errors = 0

with open(sys.argv[2], 'w') as f2:
    writer = csv.writer(f2, delimiter=delim, quoting=csv.QUOTE_NONE, quotechar=chr(255), escapechar='\\')
    with open(sys.argv[1], 'r') as f1:
        reader = csv.reader(f1, delimiter=delim, quoting=csv.QUOTE_NONE, quotechar=chr(255))
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
