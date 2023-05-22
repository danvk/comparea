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

export function renderAbout() {
  return `
  <!DOCTYPE html>
  <html>
  <head>
    <meta charset="utf-8">
    <title>Comparea</title>
    <meta name="viewport" content="initial-scale=1,user-scalable=no,maximum-scale=1">
    <link rel="stylesheet" href="/static/css/comparea.css?v={{version}}">
  </head>

  <body class="about">
  <div class="wrapper">
  <h2>About Comparea</h2>

  <p>Comparea lets you compare the area of two geographic features (continents, countries, states). Because of the projection that Comparea uses, this comparison is valid (the size of the features is proportional to their area) and suffers from minimal distortion. This lets you see just how big Greenland or Alaska <i>really</i> is.</p>

  <h3>How it works</h3>
  <p>Comparea uses two <a href="https://en.wikipedia.org/wiki/Albers_projection">Albers Equal Area conic projections</a>, centered on the <a href="https://en.wikipedia.org/wiki/Centroid">centroids</a> (centers of mass) of the two features. Because the Albers projection is <a href="http://www.progonos.com/furuti/MapProj/Dither/ProjConf/projConf.html">conformal</a> (equal area) and the two projections use the same scale, this results in a valid area comparison. And because the Albers projection minimizes distortion around its center, the feature won't be too badly mangled. This is especially true for small features, though you can see some distortion around the edges of large features.</p>

  <p>Intuitively, you can imagine that comparea takes two globes and rotates the two features to the center of each. It then applies the projections and superimposes the resulting shapes:</p>

  <a href="/USA48+GRL"><img src="/static/img/how-comparea-works.png" width=791 height=313></a>

  <h3>Background</h3>
  <p>The idea for Comparea came when I moved from San Francisco to New York City and wanted to relate new geographic features to familiar ones. I quickly found that, due to the inestimable Natural Earth Data (see below), the &ldquo;Golden Gate Park vs. Central Park&rdquo; comparison was quite a bit harder to get at than &ldquo;California vs. New York&rdquo;. This led me to sit on my initial demo for a few years. But myriad conversations where Comparea would have been helpful made me realize that I was letting <a href="https://en.wikipedia.org/wiki/Perfect_is_the_enemy_of_good">the perfect be the enemy of the good</a>. And so Comparea was released!</p>

  <h3>Acknowledgements</h3>
  <p>Comparea is completely dependent on the fabulous <a href="http://www.naturalearthdata.com/">Natural Earth Data</a> for feature outlines. Specifically, it uses a combination of:</p>

  <ul>
    <li><a href="http://www.naturalearthdata.com/downloads/50m-cultural-vectors/50m-admin-0-countries-2/">Admin 0 - Countries</a> without boundary lakes</li></li>
    <li><a href="http://www.naturalearthdata.com/downloads/50m-cultural-vectors/50m-admin-0-details/">Admin 0 - Details</a> for subunits (e.g. European/Asian Russia, North Cyprus, Somaliland)</a></li>
  <li><a href="http://www.naturalearthdata.com/downloads/50m-cultural-vectors/50m-admin-1-states-provinces/">Admin 1 – States, provinces</a> also without large lakes</a>
  </ul>

  <p>Feature descriptions come from <a href="https://www.freebase.com/m/035dk#/common/topic/description">Freebase</a>, which gets them from Wikipedia.</p>

  <p>Feature areas and populations come largely from the CIA World Factbook and the US Census, with a smattering of other sources. A reasonablely thorough effort has been made to ensure that the stated area and population are for the same feature that Comparea shows, but this may not always be precisely true. In general, if you calculate the area of the polygon that Comparea displays, it will differ by no more than 10% from the stated area.</p>

  <p>Comparea relies on a few third party libraries and services. Highlights:</p>
  <ul>
    <li>D3.js</li>
    <li>jQuery</li>
    <li>Select2</li>
    <li>Flask</li>
    <li>GDAL</li>
    <li>pyproj</li>
    <li>shapely</li>
    <li>gunicorn</li>
    <li>Cloudflare</li>
    <li>Heroku</li>
  </ul>

  <h3>Feedback / Contribute</h3>

  <p>Have a bug to report? A feature to request? <a href="https://github.com/danvk/comparea/issues/new">File it on github</a>.</p>

  <p>Have something you want to tell us about? Fill out our <a href="https://docs.google.com/forms/d/1lbGR1vsyzhxrHYlKPYwtK9b8kQzq1gqbtEtI7a4u-PM/viewform?usp=send_form">feedback form</a>.</p>

  <p>Want to play with the data yourself? Check out the project <a href="https://github.com/danvk/comparea">on github</a>, including the <a href="https://raw.githubusercontent.com/danvk/comparea/master/comparea/static/data/comparea.geo.json" download>GeoJSON file</a> containing all the shapes, statistics, descriptions and links served on Comparea.</p>


  <h3>References</h3>

  <div class="references">
  <p>"<a href="https://commons.wikimedia.org/wiki/File:Greenland_(orthographic_projection).svg#mediaviewer/File:Greenland_(orthographic_projection).svg">Greenland (orthographic projection)</a>" by <a href="//commons.wikimedia.org/wiki/User:Connormah" title="User:Connormah">Connormah</a> - <span class="int-own-work">Own work</span>. Licensed under <a href="http://creativecommons.org/licenses/by-sa/3.0
  " title="Creative Commons Attribution-Share Alike 3.0
  ">CC BY-SA 3.0</a> via <a href="//commons.wikimedia.org/wiki/">Wikimedia Commons</a>.</p>

  <p>"<a href="https://commons.wikimedia.org/wiki/File:United_States_(orthographic_projection).svg#mediaviewer/File:United_States_(orthographic_projection).svg">United States (orthographic projection)</a>" by <a href="//commons.wikimedia.org/wiki/User:Ssolbergj" title="User:Ssolbergj">Ssolbergj</a> - Own work,
  This <a href="//en.wikipedia.org/wiki/Vector_images" class="extiw" title="w:Vector images">vector image</a> was created with <a href="//commons.wikimedia.org/wiki/Help:Inkscape" title="Help:Inkscape">Inkscape</a>.
  <a rel="nofollow" class="external text" href="http://www.aquarius.geomar.de/omc/make_map.html">Aquarius.geomar.de</a>
  <span class="wpImageAnnotatorControl wpImageAnnotatorOff"><a href="//commons.wikimedia.org/wiki/File:GMT_globe.png" class="image"></a></span>
  The map has been created with the <a href="//en.wikipedia.org/wiki/Generic_Mapping_Tools" class="extiw" title="en:Generic Mapping Tools">Generic Mapping Tools</a>: <a rel="nofollow" class="external free" href="http://gmt.soest.hawaii.edu/">http://gmt.soest.hawaii.edu/</a> using one or more of these <a href="//en.wikipedia.org/wiki/Public_domain" class="extiw" title="en:Public domain">public domain</a> datasets for the relief:
  ETOPO2 (<a href="//en.wikipedia.org/wiki/topography" class="extiw" title="en:topography">topography</a>/<a href="//en.wikipedia.org/wiki/bathymetry" class="extiw" title="en:bathymetry">bathymetry</a>): <a rel="nofollow" class="external free" href="http://www.ngdc.noaa.gov/mgg/global/global.html">http://www.ngdc.noaa.gov/mgg/global/global.html</a>
  GLOBE (<a href="//en.wikipedia.org/wiki/topography" class="extiw" title="en:topography">topography</a>): <a rel="nofollow" class="external free" href="http://www.ngdc.noaa.gov/mgg/topo/gltiles.html">http://www.ngdc.noaa.gov/mgg/topo/gltiles.html</a>
  SRTM (<a href="//en.wikipedia.org/wiki/topography" class="extiw" title="en:topography">topography</a>): <a rel="nofollow" class="external free" href="http://www2.jpl.nasa.gov/srtm/">http://www2.jpl.nasa.gov/srtm/</a>
  <span style="font-size:x-small;line-height:140%" class="plainlinks noprint"><a class="external text" href="//commons.wikimedia.org/wiki/Template:GFDL-GMT/en">English</a>&nbsp;| <a class="external text" href="//commons.wikimedia.org/wiki/Template:GFDL-GMT/it">italiano</a>&nbsp;| <a class="external text" href="//commons.wikimedia.org/wiki/Template:GFDL-GMT/mk">македонски</a>&nbsp;| <a class="external text" href="//commons.wikimedia.org/wiki/Template:GFDL-GMT/ja">日本語</a>&nbsp;| <a class="external text" href="//commons.wikimedia.org/w/index.php?title=Template:GFDL-GMT/lang&amp;action=edit">+/−</a>
  </span>
  <a href="//commons.wikimedia.org/wiki/File:Heckert_GNU_white.svg" class="image" title="GNU head"></a>
  Permission is granted to copy, distribute and/or modify this document under the terms of the <a href="//en.wikipedia.org/wiki/en:GNU_Free_Documentation_License" class="extiw" title="w:en:GNU Free Documentation License">GNU Free Documentation License</a>, Version 1.2 or any later version published by the <a href="//en.wikipedia.org/wiki/en:Free_Software_Foundation" class="extiw" title="w:en:Free Software Foundation">Free Software Foundation</a>; with no Invariant Sections, no Front-Cover Texts, and no Back-Cover Texts. A copy of the license is included in the section entitled <a href="//commons.wikimedia.org/wiki/Commons:GNU_Free_Documentation_License_1.2" title="Commons:GNU Free Documentation License 1.2" class="mw-redirect">GNU Free Documentation License</a>.. Licensed under <a href="http://creativecommons.org/licenses/by/3.0
  " title="Creative Commons Attribution 3.0
  ">CC BY 3.0</a> via <a href="//commons.wikimedia.org/wiki/">Wikimedia Commons</a>.</p>
  </div>

  </div>

  ${renderAnalytics()}
  </body>

  </html>
`;
}
