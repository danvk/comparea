from . import app
from . import models
from flask import render_template, jsonify, request

import sys

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

    return render_template('index.html',
            shape1=shape1,
            shape2=shape2,
            name_id_pairs=name_id_pairs,
            use_third_party_cdn=app.config['USE_THIRD_PARTY_CDN'])


@app.route('/shape/<shape_id>')
def get_shape(shape_id):
    shape = models.feature_for_code(shape_id)
    if not shape:
        return "No feature with id %s" % shape_id, 400

    d = {
        'panel': render_template('panel.html', shape=shape),
        'feature': shape
    }

    other_shape_id = request.args.get('other_shape')
    sys.stderr.write('Other shape id %s\n' % other_shape_id)
    if other_shape_id:
        shape_idx = request.args.get('shape_index')
        sys.stderr.write('Shape index %s\n' % shape_idx)
        other_shape = models.feature_for_code(other_shape_id)
        if not other_shape:
            return "No feature with id %s" % other_shape_id, 400
        if shape_idx == '0':
            shape1, shape2 = shape, other_shape
        else:
            shape1, shape2 = other_shape, shape
        d['comparison'] = (
            render_template('comparison.html', shape1=shape1, shape2=shape2))

    return jsonify(d)


@app.route('/reloadfish', methods=['POST'])
def reloadfish():
    if app.config['DEBUG']:
        models.reload_data()
    return "OK"


@app.route('/about')
def about():
    return render_template('about.html')
