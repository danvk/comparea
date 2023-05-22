import safeHtml from 'html-template-tag';
import { sprintf } from 'sprintf-js';

import { CompareaFeature } from './api';
import { sortKeys } from './util';

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

export interface PageData {
  title: string;
  shape1: CompareaFeature;
  shape2: CompareaFeature;
  nameIdPairs: readonly [string, string][];
  useThirdPartyCdn: boolean;
}

export function renderHTML({
  title,
  shape1,
  shape2,
  nameIdPairs,
  useThirdPartyCdn,
}: PageData): string {
  const jsBlock = useThirdPartyCdn
    ? `
<link rel="stylesheet" href="//cdnjs.cloudflare.com/ajax/libs/select2/3.5.0/select2.min.css">
<script src="//cdnjs.cloudflare.com/ajax/libs/d3/3.4.11/d3.min.js"></script>
<script src="//ajax.googleapis.com/ajax/libs/jquery/2.1.1/jquery.min.js"></script>
<script src="//cdnjs.cloudflare.com/ajax/libs/select2/3.5.0/select2.min.js"></script>
  `
    : `
<link rel="stylesheet" href="/static/lib/select2.min.css">
<script src="/static/lib/d3.min.js"></script>
<script src="/static/lib/jquery.min.js"></script>
<script src="/static/lib/select2.min.js"></script>
  `;

  const optionsHTML = (selectedId: string | number | undefined) =>
    nameIdPairs
      .map(
        ([name, id]) =>
          safeHtml`<option ${
            id === selectedId ? 'selected ' : ''
          }value="${id}">${name}</option>`
      )
      .join('\n\n');

  return safeHtml`
<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8">
<title>$${title}</title>
<meta name="viewport" content="minimal-ui, user-scalable=0, initial-scale=1.0">
<meta name="apple-mobile-web-app-capable" content="yes" />
<meta property="fb:admins" content="3001252" />
<link rel="icon" sizes="256x256" href="/static/img/comparea256.png">
<link rel="icon" sizes="32x32" href="/static/img/comparea32.png">
<link rel="apple-touch-icon" href="/static/img/comparea256.png" />
<link rel="shortcut icon" href="/static/img/comparea32.png">

<link rel="stylesheet" href="/static/css/comparea.css">

$${jsBlock}
</head>

<body>

<div class="size-comparison-holder">
<p class="size-comparison">$${renderComparison(shape1, shape2)}</p>
</div>

<div id="svg-container"></div>

<div id="sidebar">
  <div class='side-panel' id='side-panel0'>
    <select class="choose" id="choose0">
      $${optionsHTML(shape1.id)}
    </select>
    <div class="feature-panel">$${renderPanel(shape1)}</div>
  </div>
  <div class='side-panel' id='side-panel1'>
    <select class="choose" id="choose1">
    $${optionsHTML(shape2.id)}
    </select>
    <div class="feature-panel">$${renderPanel(shape2)}</div>
  </div>

  <a class="about-link" href="/about">About</a>
  <div class="size-comparison">$${renderComparison(shape1, shape2)}</div>
</div>

<div id="feedback"><a href="https://docs.google.com/forms/d/1lbGR1vsyzhxrHYlKPYwtK9b8kQzq1gqbtEtI7a4u-PM/viewform?usp=send_form" target="_blank">Send feedback</a></div>

<script type="text/javascript">
var geojson_features = [
    $${JSON.stringify(sortKeys(shape1))},
    $${JSON.stringify(sortKeys(shape2))}
  ];
</script>

<script src="/static/js/packer.js"></script>
<script src="/static/js/comparea.js"></script>
<script src="/static/js/render.js"></script>

$${renderAnalytics()}
</body>
</html>
  `;
}

export function renderAnalytics() {
  return `
<script async src="https://www.googletagmanager.com/gtag/js?id=G-8WVHY30T4T"></script>
<script>
  window.dataLayer = window.dataLayer || [];
  function gtag(){dataLayer.push(arguments);}
  gtag('js', new Date());

  gtag('config', 'G-8WVHY30T4T');
</script>
`;
}
