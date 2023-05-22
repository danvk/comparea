import { Feature, FeatureCollection, Polygon, MultiPolygon } from 'geojson';

export interface CompareaProperties {
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

export type CompareaFeature = Feature<
  Polygon | MultiPolygon,
  CompareaProperties
>;
export interface ShapeRequest {
  other_shape: string;
  shape_index: number;
}
export interface ShapeResponseBase {
  panel: string;
  feature: CompareaFeature;
}
export interface ComparisonResponse extends ShapeResponseBase {
  comparison: string;
  title: string;
}
