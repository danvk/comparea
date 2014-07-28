'''Load area and population data from a spreadsheet.

The spreadsheet lives in Google Docs & must be manually exported to
data/comparea-spreadsheet.csv before use.
'''
import os
import csv
import copy

DATA = None

def _path(filename):
    return os.path.join(os.path.dirname(__file__), filename)


def _load_data():
    global DATA
    DATA = {}

    for row in csv.DictReader(open(_path('comparea-spreadsheet.csv'))):
        if not row['Name']: continue  # blank or header line

        pop = row['population']
        pop = int(pop.replace(',', ''))
        row['population'] = pop

        area = row['area_km2']
        area = int(float(area.replace(',', '')))
        row['area_km2'] = area

        code = row['Code']
        del row['Code']
        del row['Name']
        DATA[code] = row


def get_feature_data(code):
    if not DATA:
        _load_data()

    if code not in DATA:
        raise KeyError('%s missing from spreadsheet data' % code)

    return copy.deepcopy(DATA[code])
