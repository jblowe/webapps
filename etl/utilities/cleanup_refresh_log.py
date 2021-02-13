import sys, csv
from datetime import datetime, date, time

'''
parses refresh.log, the log of solr core refreshes kept under app_solr, to make it
easily parseable by solr-core-stats.ipynb
'''

with open(sys.argv[2], "w") as out:
    writer = csv.writer(out, delimiter="\t")
    with open(sys.argv[1], "r") as original:
        reader = csv.reader(original, delimiter=",")
        for i, row in enumerate(reader):
            if len(row) != 3 or not 'rows' in row[2]: continue
            if 'PROBLEM' in row[1]: continue
            row[2] = str(int(row[2].replace(' rows','')))
            row[1] = row[1].replace(' PST','').replace(' PDT','')
            dt = datetime.strptime(row[1], "%c")
            row[1] = dt.strftime('%Y-%m-%d')
            #dt = datetime.strptime(row[1], "%a %d %b %H:%M:%S %Y")
            # 'Sun Dec  4 04:12:20 PST 2016'
            writer.writerow(row)
