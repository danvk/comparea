import express from 'express';
import fs from 'fs';
import { Feature, FeatureCollection, Polygon, MultiPolygon } from 'geojson';
import {
  CompareaFeature,
  CompareaProperties,
  ComparisonResponse,
  ShapeResponseBase,
} from './api';
import { pageTitle, renderPanel } from './templates';
import { sortKeys } from './util';

const app = express();
app.set('extended', false);
app.set('json spaces', 2);
const port = 3000;

const features = JSON.parse(
  fs.readFileSync('comparea/static/data/comparea.geo.json', 'utf-8')
) as FeatureCollection<Polygon | MultiPolygon, CompareaProperties>;
const idToFeature: Record<string, CompareaFeature> = {};
for (const f of features.features) {
  if (!f.id) {
    throw new Error('Invalid features, missing ID.');
  }
  idToFeature[f.id] = f;
}

app.get('/', (req, res) => {
  res.send('Hello World!');
});

app.get('/shape/:shapeId', (req, res) => {
  const { shapeId } = req.params;
  const f = idToFeature[shapeId];
  if (!f) {
    res.status(400).send(`No feature with ID ${shapeId}`);
    return;
  }

  const response: ShapeResponseBase = {
    panel: renderPanel(f),
    feature: f,
  };

  const otherShapeId = req.query['other_shape'] as string | undefined;
  if (otherShapeId) {
    const otherFeature = idToFeature[otherShapeId];
    if (!otherFeature) {
      res.status(400).send(`No feature with ID ${otherShapeId}`);
      return;
    }
    const shapeIndex = req.query['shape_index'] as string;
    let shape1: CompareaFeature, shape2: CompareaFeature;
    if (shapeIndex === '0') {
      [shape1, shape2] = [f, otherFeature];
    } else {
      [shape1, shape2] = [otherFeature, f];
    }

    const comparisonResponse: ComparisonResponse = {
      ...response,
      comparison: renderComparison(shape1, shape2),
      title: pageTitle(shape1, shape2),
    };
    res.json(sortKeys(comparisonResponse));
  }
  res.json(sortKeys(response));
});

app.listen(port, () => {
  console.log(`Example app listening on port ${port}`);
});
