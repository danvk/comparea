import safeHtml from 'html-template-tag';

import { CompareaFeature } from './api';

export function renderPanel(f: CompareaFeature): string {
  return safeHtml`<p>Name: ${f.properties.name}</p>`;
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
