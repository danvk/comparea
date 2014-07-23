import os

POPULATION = None
AREA = None
POPULATION_URL = 'https://www.cia.gov/library/publications/the-world-factbook/fields/2119.html'
AREA_URL = 'https://www.cia.gov/library/publications/the-world-factbook/fields/2147.html'

def _path(filename):
    return os.path.join(os.path.dirname(__file__), filename)

def _load_data():
    global POPULATION, AREA
    POPULATION = {}
    for idx, line in enumerate(open(_path('cia-population.txt'))):
        if idx == 0: continue  # skip header
        fields = line.strip().split('\t')
        if len(fields) < 5: continue

        su_a3 = fields[0]
        pop_date = fields[4]
        try:
            pop = fields[3]
            pop = int(pop.replace(',', ''))
        except ValueError:
            raise ValueError('Bad population %s for %s' % (pop, su_a3))

        if su_a3 in POPULATION:
            if pop < POPULATION[su_a3]['population']:
                # Probably a constituent territoriy, e.g. a US Minor Island.
                continue

        POPULATION[su_a3] = {
            'population': pop,
            'population_date': pop_date
        }

    AREA = {}
    for idx, line in enumerate(open(_path('cia-area.txt'))):
        if idx == 0: continue  # skip header
        fields = line.strip().split('\t')
        if len(fields) < 7: continue
        su_a3 = fields[0]
        try:
            area = fields[6]
            area = float(area.replace(',', ''))
            if area == round(area):
                area = int(area)
        except ValueError:
            raise ValueError('Bad area %s for %s' % (fields[6], su_a3))

        if su_a3 in AREA:
            if area < AREA[su_a3]:
                continue  # see above

        AREA[su_a3] = area


def get_country_data(su_a3_code):
    if not POPULATION or not AREA:
        _load_data()

    if su_a3_code not in POPULATION or su_a3_code not in AREA:
        raise KeyError('%s missing from CIA data' % su_a3_code)

    pop_data = POPULATION[su_a3_code]
    area = AREA[su_a3_code]

    return {
        'population': pop_data['population'],
        'population_date': pop_data['population_date'],
        'population_source': 'World Factbook',
        'population_source_url': POPULATION_URL,
        'area_km2': area,
        'area_km2_source': 'World Factbook',
        'area_km2_source_url': AREA_URL
    }
