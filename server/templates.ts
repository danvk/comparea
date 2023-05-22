import safeHtml from 'html-template-tag';
import { sprintf } from 'sprintf-js';

import { CompareaFeature } from './api';

/** Returns a string like '10%' or '123 times'. Assumes ratio>1. */
export function formatRatio(ratio: number): string {
  if (ratio < 2) {
    return sprintf('%.2g%%', 100 * (ratio - 1));
  } else if (ratio < 100) {
    return sprintf('%.2g times', ratio);
  }
  return Math.round(ratio).toLocaleString() + ' times';
}

export function renderComparison(
  f1: CompareaFeature,
  f2: CompareaFeature,
  flipped = false
): string {
  const props1 = f1.properties;
  const props2 = f2.properties;
  if (props1.area_km2 < props2.area_km2) {
    return renderComparison(f2, f1, true);
  }

  const class1 = 'feature' + (flipped ? '2' : '1');
  const class2 = 'feature' + (flipped ? '1' : '2');
  const ratio = formatRatio(props1.area_km2 / props2.area_km2);
  return safeHtml`
    <span class="${class1}">${props1.name}</span> is
    ${ratio} larger than
    <span class="${class2}">${props2.name}</span>.
  `;
}

export function pageTitle(f1: CompareaFeature, f2: CompareaFeature): string {
  const name1 = f1.properties.name;
  const name2 = f2.properties.name;
  return `${name1} vs. ${name2}: Comparea Area Comparison`;
}

export function renderPanel(f: CompareaFeature): string {
  const props = f.properties;
  return safeHtml`
<div class="statistics">
  <p>
    <span class=stat-name>Area</span>:
    <span class="stat-value area">${Math.round(
      props.area_km2
    ).toLocaleString()} km<sup>2</sup></span>
    <a class="stat-source" href="${props.area_km2_source_url}">${
    props.area_km2_source
  }</a>
  </p>
  <p class="population">
    <span class="stat-name">Population</span>:
    <span class="stat-value">${Math.round(
      props.population
    ).toLocaleString()}</span>
    (<span class="stat-year">${props.population_date}</span>)
    <a class="stat-source" href="${props.population_source_url}">${
    props.population_source
  }</a>
   </p>
</div>
<p class="description">
  ${props.description}
  <a href="${props.wikipedia_url}">Wikipedia</a>
</p>
  `;
}
