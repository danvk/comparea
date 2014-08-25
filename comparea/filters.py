from . import app

@app.template_filter()
def format_commas(num):
    '''Format an int with commas: 1,234,567'''
    return "{:,d}".format(num)

@app.template_filter()
def format_ratio(ratio):
    '''Returns a string like '10%' or '123 times'. Assumes ratio>1'''
    if ratio < 2:
        return '%.2g%%' % (100.0 * (ratio - 1))
    elif ratio < 100:
        return '%.2g times' % ratio
    else:
        return '{:,d} times'.format(int(round(ratio)))
