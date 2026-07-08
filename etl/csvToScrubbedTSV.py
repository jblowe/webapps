#
# convert a properly-quoted CSV into a plain, unencapsulated TSV: scrub
# tab/\r/\n out of every field first (collapsed to a single space) so no
# encapsulation is needed -- every field is read correctly regardless of
# what it contained, since this reads the already-correct CSV rather than
# re-deriving row/column boundaries from scratch.
#
# usage: python3 csvToScrubbedTSV.py input.csv output.tsv
#

import sys, csv, re

infile, outfile = sys.argv[1], sys.argv[2]

scrub = re.compile(r'[\t\r\n]+')

with open(infile, newline='') as f:
    reader = csv.reader(f)
    with open(outfile, 'w', newline='') as out:
        for row in reader:
            out.write('\t'.join(scrub.sub(' ', cell) for cell in row) + '\n')
