from . import app
from . import models
from flask import render_template, jsonify

@app.route('/')
def index():
    return pair('USA48', 'AUS')


@app.route('/<id1>+<id2>')
def pair(id1, id2):
    shape1 = models.feature_for_code(id1)
    shape2 = models.feature_for_code(id2)
    name_id_pairs = models.all_countries()

    if not shape1:
        return "No feature with id %s" % id1, 400
    if not shape2:
        return "No feature with id %s" % id2, 400

    return render_template('index.html', shape1=shape1, shape2=shape2, name_id_pairs=name_id_pairs)


@app.route('/shape/<shape_id>')
def get_shape(shape_id):
    shape = models.feature_for_code(shape_id)
    if not shape:
        return "No feature with id %s" % shape_id, 400

    return jsonify({
        'panel': render_template('panel.html', shape=shape),
        'feature': shape
    })


@app.route('/reloadfish', methods=['POST'])
def reloadfish():
    if app.config['DEBUG']:
        models.reload_data()
    return "OK"


@app.route('/about')
def about():
    return render_template('about.html')
