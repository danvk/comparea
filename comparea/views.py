from . import app
from . import models
from flask import render_template

@app.route('/')
def index():
    return pair('USA', 'AUS')

@app.route('/<id1>+<id2>')
def pair(id1, id2):
    shape1 = models.feature_for_iso3(id1)
    shape2 = models.feature_for_iso3(id2)
    name_id_pairs = models.all_countries()

    if not shape1:
        return "No feature with id %s" % id1, 400
    if not shape2:
        return "No feature with id %s" % id2, 400

    return render_template('index.html', shape1=shape1, shape2=shape2, name_id_pairs=name_id_pairs)
