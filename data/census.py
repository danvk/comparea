import os

POPULATION = None
AREA = None

POPULATION_URL = 'http://www.census.gov/popest/data/state/totals/2013/index.html'
AREA_URL = 'http://www.census.gov/prod/cen2010/cph-2-1.pdf'

def _path(filename):
    return os.path.join(os.path.dirname(__file__), filename)


def _load_data():
    global POPULATION, AREA
    POPULATION = {}
    for idx, line in enumerate(open(_path('census-population.txt'))):
        if idx == 0: continue  # skip header
        fields = line.strip().split('\t')
        if len(fields) < 2: continue

        code = fields[0]
        try:
            pop = fields[1]
            pop = int(pop.replace(',', ''))
        except ValueError:
            raise ValueError('Bad population %s for %s' % (pop, code))

        assert code not in POPULATION
        POPULATION[code] = pop

    AREA = {}
    for idx, line in enumerate(open(_path('census-area.txt'))):
        if idx == 0: continue  # skip header
        fields = line.strip().split('\t')
        if len(fields) < 2: continue
        code = fields[0]
        try:
            area = fields[1]
            area = int(area.replace(',', ''))
        except ValueError:
            raise ValueError('Bad area %s for %s' % (area, code))

        assert code not in AREA
        AREA[code] = area


def get_state_data(code):
    if not POPULATION or not AREA:
        _load_data()

    if code not in POPULATION or code not in AREA:
        raise KeyError('%s missing from census data' % code)

    pop = POPULATION[code]
    area = AREA[code]

    return {
        'population': pop,
        'population_date': 'July 2013',
        'population_source': 'US Census',
        'population_source_url': POPULATION_URL,
        'area_km2': area,
        'area_km2_source': 'US Census',
        'area_km2_source_url': AREA_URL
    }
