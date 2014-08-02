// Percentage gap to leave between shapes for horizontal/vertical packing.
var ADJACENT_PACK_PADDING = 0.1;

// Threshold for switching between horizontal/vertical packing and overlap
// packing.
var MIN_RATIO_FOR_OVERLAP_PACKING = 4;

// Converts [[t,l], [b,r]] array to {width, height} array.
function boundsToSpans(bounds) {
  return bounds.map(function(b, i) {
    return {
      left: b[0][0],
      right: b[1][0],
      top: b[0][1],
      bottom: b[1][1],
      width: b[1][0] - b[0][0],
      height: b[1][1] - b[0][1],
      centerX: (b[1][0] + b[0][0])/2,
      centerY: (b[1][1] + b[0][1])/2
    }
  });
}


// Add offsets to the spans, returning new spans.
function offsetSpans(spans, offsets) {
  return spans.map(function(span, i) {
    var offset = offsets[i];
    return {
      left: span.left + offset.x,
      right: span.right + offset.x,
      top: span.top + offset.y,
      bottom: span.bottom + offset.y,
      width: span.width,
      height: span.height,
      centerX: span.centerX + offset.x,
      centerY: span.centerY + offset.y
    };
  });
}


/**
 * Places the centroids of the features along the main (TL to BR) diagonal.
 */
function diagonalPacker(svgArea, spans) {
  // bounding boxes for the features under the current projections
  var DIR_X = 0, DIR_Y = 1; 

  // This defines a line mapping a param, t \in [0, 1], to the main diagonal.
  var svgScaleX = d3.scale.linear().domain([0,1]).range([0, svgArea.width]),
      svgScaleY = d3.scale.linear().domain([0,1]).range([0, svgArea.height]);

  // start with a guess for placement -- we'll adjust momentarily.
  var centroidsT = [0.25, 0.75];

  // compute the gap (or overlap) between the two features along the main
  // diagonal. We could be limited by either dimension, so we compute both.
  var yGapT = svgScaleY.invert(
          (svgScaleY(centroidsT[1]) - spans[1].height / 2 + spans[1].centerY) -
          (svgScaleY(centroidsT[0]) + spans[0].height / 2 + spans[0].centerY)),
      xGapT = svgScaleX.invert(
          (svgScaleX(centroidsT[1]) - spans[1].width / 2 + spans[1].centerX) -
          (svgScaleX(centroidsT[0]) + spans[0].width / 2 + spans[0].centerX)),
      dir = xGapT < yGapT ? DIR_X : DIR_Y,
      tGap = Math.min(xGapT, yGapT);

  centroidsT[0] += tGap / 2;
  centroidsT[1] -= tGap / 2;

  var offsets = [
      {x: svgScaleX(centroidsT[0]), y: svgScaleY(centroidsT[0])},
      {x: svgScaleX(centroidsT[1]), y: svgScaleY(centroidsT[1])} ];

  return adjustLayoutToFit(svgArea, spans, offsets);
}


/**
 * Put the two shapes right on top of one another, expanded/shrunk to fit.
 */
function overlappingPacker(svgArea, spans) {
  // Stick the two shapes on top of one another in the center.
  var cx = svgArea.width / 2, cy = svgArea.height / 2;
  return adjustLayoutToFit(
      svgArea,
      spans,
      [{x: cx, y: cy}, {x: cx, y: cy}]);
}


/**
 * Like overlappingPacker, but attempts to scootch the shapes away from one
 * another without affecting the scale.
 */
function scootchedOverlappingPacker(svgArea, spans) {
  var layout = overlappingPacker(svgArea, spans);
  spans.forEach(function(span) {
    for (var k in span) {
      span[k] *= layout.scaleMult;
    }
  });

  var cx = svgArea.width / 2, cy = svgArea.height / 2;

  // The first shape may move up or left.
  layout.offsets[0].y -= Math.max(0, cy + spans[0].top);
  layout.offsets[0].x -= Math.max(0, cx + spans[0].left);

  // The second shape may move right or down.
  layout.offsets[1].y += Math.max(0, svgArea.height - (cy + spans[1].bottom));
  layout.offsets[1].x += Math.max(0, svgArea.width - (cx + spans[1].right));

  return layout;
}


/**
 * Takes offsets which may put the shapes off-screen, or may not fully utilize
 * screen space and rescales so that the shapes snugly fit the svg area.
 * Returns a Layout object.
 */
function adjustLayoutToFit(svgArea, origSpans, offsets) {
  var spans = offsetSpans(origSpans, offsets);

  var cs = {
    left: Math.min(spans[0].left, spans[1].left),
    right: Math.max(spans[0].right, spans[1].right),
    top: Math.min(spans[0].top, spans[1].top),
    bottom: Math.max(spans[0].bottom, spans[1].bottom)
  };
  var cx = svgArea.width / 2, cy = svgArea.height / 2;

  var scaleMults = [
    /* left */  cx / (cx - cs.left),
    /* right */ cx / (cs.right - cx),
    /* top */   cy / (cy - cs.top),
    /* bot. */  cy / (cs.bottom - cy)
  ];
  var scaleMult = Math.min.apply(null, scaleMults);

  return {
    offsets: offsets.map(function(o) {
      return {
        x: cx + (o.x - cx) * scaleMult,
        y: cy + (o.y - cy) * scaleMult
      };
    }),
    scaleMult: scaleMult
  };
}

/**
 * Places the shapes side-by-side, with their centroids vertically aligned.
 */
function horizontalPacker(svgArea, spans) {
  var cx = svgArea.width / 2, cy = svgArea.height / 2;
  var totalWidth = spans[0].width + spans[1].width;
  var padding = totalWidth * ADJACENT_PACK_PADDING;

  var offsets = [
    {x: cx - spans[0].right - padding/2, y: cy},
    {x: cx - spans[0].left + padding/2, y: cy}
  ];
  return adjustLayoutToFit(svgArea, spans, offsets);
}


/**
 * Places the shapes on top of one another, with their centroids horizontally
 * aligned.
 */
function verticalPacker(svgArea, spans) {
  var cx = svgArea.width / 2, cy = svgArea.height / 2;
  var totalHeight = spans[0].height + spans[1].height;
  var padding = totalHeight * ADJACENT_PACK_PADDING;

  var offsets = [
    {x: cx, y: cy - spans[0].bottom - padding/2},
    {x: cx, y: cy - spans[0].top + padding/2}
  ];
  return adjustLayoutToFit(svgArea, spans, offsets);
}


/**
 * Modifies a packer to add some amount of padding along the edges.
 */
function insetPacker(packer, paddingPercentage) {
  return function(svgArea, spans, features) {
    var shrunkSvgArea = {
      width: (1 - paddingPercentage) * svgArea.width,
      height: (1 - paddingPercentage) * svgArea.height
    };
    var layout = packer(shrunkSvgArea, spans, features);
    layout.offsets.forEach(function(offset) {
      offset.x += paddingPercentage * svgArea.width / 2;
      offset.y += paddingPercentage * svgArea.height / 2;
    });
    return layout;
  };
}

/**
 * Adjusts a packer to account for "left" and "top" properties in svgArea.
 */
function offsetPacker(packer) {
  return function(svgArea, spans, features) {
    var layout = packer(svgArea, spans, features);
    layout.offsets.forEach(function(offset) {
      offset.x += svgArea.left;
      offset.y += svgArea.top;
    });
    return layout;
  };
}

/**
 * Overall packing strategy:
 * - For similarly-sized shapes, use horizontal or vertical packing.
 * - For skewed comparisons, use overlap packing.
 */
function combinedPacker(svgArea, spans, features) {
  var areas = features.map(function(f) { return f.properties.area_km2; });

  var ratio = Math.max(areas[1] / areas[0], areas[0] / areas[1]);
  var layout;
  if (ratio < MIN_RATIO_FOR_OVERLAP_PACKING) {
    // use horizontal/vertical.
    var h = horizontalPacker(svgArea, spans),
        v = verticalPacker(svgArea, spans);
    layout = h.scaleMult < v.scaleMult ? v : h;
  } else {
    layout = overlappingPacker(svgArea, spans);
    layout.topShapeIndex = areas[0] < areas[1] ? 0 : 1;
  }

  return layout;
}
