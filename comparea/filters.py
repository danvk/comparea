from . import app

@app.template_filter()
def format_commas(num):
    '''Format an int with commas: 1,234,567'''
    return "{:,d}".format(num)
