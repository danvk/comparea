from . import app
from . import models
from flask import render_template

@app.route('/')
def index():
    shape1 = models.feature_for_iso3('AUS')
    shape2 = models.feature_for_iso3('USA')
    name_id_pairs = models.all_countries()
    return render_template('index.html', shape1=shape1, shape2=shape2, name_id_pairs=name_id_pairs)
