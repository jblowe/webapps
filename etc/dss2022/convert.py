import csv
import sys

txt_file = sys.argv[1]
csv_file = sys.argv[2]

with open(txt_file, "r") as in_text:
    in_reader = csv.reader(in_text, delimiter = '\t')
    with open(csv_file, "w") as out_csv:
        out_writer = csv.writer(out_csv)
        for row in in_reader:
            out_writer.writerow(row)

