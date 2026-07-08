import sys, csv

delim = ","

inputFile1 = sys.argv[1]
inputFile2 = sys.argv[2]

f1 = csv.reader(open(inputFile1, 'r', newline=''), delimiter=delim, quoting=csv.QUOTE_MINIMAL)
f2 = csv.reader(open(inputFile2, 'r', newline=''), delimiter=delim, quoting=csv.QUOTE_MINIMAL)

file1 = {}
alreadyseen = {}
counts = {}
max = 0

counts['file1'] = 0
counts['file2'] = 0
counts['unmatched'] = 0
counts['matched'] = 0
counts['duplicates'] = 0

for lineno, ci in enumerate(f1):
    counts['file1'] += 1
    file1[ci[0]] = ci[1:]

for lineno, ci in enumerate(f2):
    # print lineno,"\t",ci
    counts['file2'] += 1
    if ci[0] in file1:
        if ci[0] in alreadyseen:
            # print('%s already seen, not added' % ci[0])
            counts['duplicates'] += 1
        else:
            alreadyseen[ci[0]] = ci
            file1[ci[0]] = file1[ci[0]] + ci[1:]
            max = len(file1[ci[0]])
            counts['matched'] += 1
    else:
        # non matching lines in file to go into the bit bucket
        counts['unmatched'] += 1
        pass

# csv.writer defaults to \r\n regardless of platform; force \n to match psql
# --csv and Text::CSV upstream/downstream, or a quoted last field ends up
# with a stray \r right after its closing quote.
writer = csv.writer(sys.stdout, delimiter=delim, quoting=csv.QUOTE_MINIMAL, lineterminator='\n')
for key, line in file1.items():
    writer.writerow([key] + line + [''] * (max - len(line)))

counts['max'] = max
for stat, value in sorted(counts.items()):
    print("%s: %s" % (stat, value), file=sys.stderr)
