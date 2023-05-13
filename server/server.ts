import express from 'express';
import fs from 'fs';
import { Feature, FeatureCollection, Polygon, MultiPolygon } from 'geojson';

interface CompareaProperties {
  name: string;
  description: string;
  freebase_mid: string;
  wikipedia_url: string;

  // These fields are always set but may be 0 or "".
  area_km2: number;
  area_km2_source: string;
  area_km2_source_url: string;

  population: number;
  population_date: string;
  population_source: string;
  population_source_url: string;
}

type CompareaFeature = Feature<Polygon | MultiPolygon, CompareaProperties>;
interface ShapeRequest {
  other_shape: string;
  shape_index: number;
}
interface ShapeResponseBase {
  panel: string;
  feature: CompareaFeature;
}
interface ComparisonResponse extends ShapeResponseBase {
  comparison: string;
  title: string;
}

const app = express();
app.set('extended', false);
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
  }

  const response: ShapeResponseBase = {
    panel: '',
    feature: f,
  };

  const otherShapeId = req.query['other_shape'] as string | undefined;
  if (otherShapeId) {
    const otherFeature = idToFeature[otherShapeId];
    if (!otherFeature) {
      res.status(400).send(`No feature with ID ${otherShapeId}`);
    }
    const shapeIndex = req.query['shape_index'] as string;

    const comparisonResponse: ComparisonResponse = {
      ...response,
      comparison: '',
      title: 'page title',
    };
    res.json(comparisonResponse);
  }
  res.json(response);
});

app.listen(port, () => {
  console.log(`Example app listening on port ${port}`);
});
