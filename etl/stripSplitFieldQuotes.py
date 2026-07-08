#
# Solr's CSV loader mis-parses a field configured with f.<field>.split=true
# when that field's value contains a literal double-quote with more content
# after it (e.g. `Grandfather" O.R. at ...`) -- it mistakes the escaped
# quote pair for the field's real closing quote and chokes on whatever
# follows with "invalid char between encapsulated token end delimiter".
# Confirmed as a genuine Solr bug (reproduced on 9.4.0 and 9.9.0), not
# something we can fix on our end, so neutralize the trigger instead:
# replace literal " with ' in exactly the columns genschema.sh configures
# for split=true (every _ss field except blob_ss -- same rule, kept in
# sync so a newly added _ss field is covered automatically).
#
# usage: python3 stripSplitFieldQuotes.py input.csv output.csv
#

import sys, csv

infile, outfile = sys.argv[1], sys.argv[2]

with open(infile, newline='') as f:
    rows = list(csv.reader(f))

header = rows[0]
target_cols = [i for i, name in enumerate(header) if name.endswith('_ss') and 'blob' not in name]

with open(outfile, 'w', newline='') as f:
    writer = csv.writer(f, lineterminator='\n')
    writer.writerow(header)
    for row in rows[1:]:
        for i in target_cols:
            if '"' in row[i]:
                row[i] = row[i].replace('"', "'")
        writer.writerow(row)
