import sys, csv

delim = ','


def get_date_rows(row):
    date_rows = []
    for i, r in enumerate(row):
        if "objectproductionscalardate_ss" in r:
            row.append(r.replace('_ss', '_i'))
            date_rows.append(i)
    return date_rows


def get_year(date_value):
    year = date_value[0:4]
    try:
        year_int = int(year)
    except ValueError:
        return ''
    if year_int < 1500 or year_int > 2025:
        return ''
    return year


with open(sys.argv[2], 'w', newline='') as f2:
    # force \n: csv.writer defaults to \r\n, which doesn't match psql --csv
    file_with_integer_times = csv.writer(f2, delimiter=delim, quoting=csv.QUOTE_MINIMAL, lineterminator='\n')
    with open(sys.argv[1], 'r', newline='') as f1:
        reader = csv.reader(f1, delimiter=delim, quoting=csv.QUOTE_MINIMAL)
        try:
            for i, row in enumerate(reader):
                if i == 0:
                    date_rows = get_date_rows(row)
                else:
                    for d in date_rows:
                        row.append(get_year(row[d]))
                file_with_integer_times.writerow(row)
        except:
            # really someday we should do something better than just die here...
            raise
