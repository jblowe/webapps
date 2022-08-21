#

import sys, csv, collections
import requests
from collections import Counter
from wand.image import Image

delim = "\t"

imageserver_url = 'http://10.161.2.194:8080/omca/imageserver/blobs/%s/content'

types = {}
errors = 0

with open(sys.argv[2], 'w') as f2:
    writer = csv.writer(f2, delimiter=delim, quoting=csv.QUOTE_NONE, quotechar=chr(255), escapechar='\\')
    with open(sys.argv[1], 'r') as f1:
        reader = csv.reader(f1, delimiter=delim, quoting=csv.QUOTE_NONE, quotechar=chr(255))
        for lineno, row in enumerate(reader):
            if lineno == 0:
                header = row
                writer.writerow(row + ['format', 'width', 'height'])
                for col in header:
                    types[col] = Counter()
                column_count = len(header)
            else:
                headers = {}
                blob_csid = row[7]
                url = imageserver_url % blob_csid
                info = requests.get(url, headers=headers)
                image = info.content
                try:
                    with Image(blob=image) as img:
                        # print('format =', img.format)
                        # print('size =', img.size)
                        row = row + [img.format] + list(img.size)
                except:
                    row = row + ['invalid', '-1', '-1']
                    # raise

                writer.writerow(row)

if errors > 0:
    print
    print("%s errors seen (i.e. data row and header row w different counts.)" % errors)
    print

print("%s\t%s\t%s" % ('column', 'types', 'tokens'))
try:
    for key in header:
        print("%s\t%s\t%s" % (key, len(types[key]), sum(types[key].values())))
except:
    print('evaluation incomplete: something went wrong -- empty file? not csv?')