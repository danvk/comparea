import _ from 'lodash';
import express from 'express';
import fs from 'fs';
import { Feature, FeatureCollection, Polygon, MultiPolygon } from 'geojson';
import {
  CompareaFeature,
  CompareaProperties,
  ComparisonResponse,
  ShapeResponseBase,
} from './api';
import {
  pageTitle,
  renderComparison,
  renderHTML,
  renderPanel,
} from './templates';
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
const nameIdPairs = _.sortBy(
  Object.entries(idToFeature).map(
    ([id, f]) => [f.properties.name, id] as [string, string]
  ),
  ([name, id]) => name,
  ([name, id]) => id
);

app.get('/', (req, res) => {
  res.send('Hello World!');
});

app.get('/:shape1\\+:shape2', (req, res) => {
  const { shape1, shape2 } = req.params as unknown as {
    shape1: string;
    shape2: string;
  };

  const f1 = idToFeature[shape1];
  if (!f1) {
    return res.status(400).send(`No feature with ID ${shape1}`);
  }
  const f2 = idToFeature[shape2];
  if (!f2) {
    return res.status(400).send(`No feature with ID ${shape2}`);
  }

  res.send(
    renderHTML({
      title: pageTitle(f1, f2),
      shape1: f1,
      shape2: f2,
      nameIdPairs,
      useThirdPartyCdn: false,
    })
  );
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

app.use('/static', express.static('comparea/static'));

app.listen(port, () => {
  console.log(`Example app listening on port ${port}`);
});
