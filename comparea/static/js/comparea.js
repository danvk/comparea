// See http://stackoverflow.com/questions/14167863/how-can-i-bring-a-circle-to-the-front-with-d3
d3.selection.prototype.moveToFront = function() {
  return this.each(function(){
    this.parentNode.appendChild(this);
  });
};

var width = document.getElementById('svg-container').offsetWidth,
    height = document.getElementById('svg-container').offsetHeight;

var svg = d3.select("#svg-container").append("svg")
    .attr("width", width)
    .attr("height", height);
svg.append('g')
    .attr('class', 'container');


function projectionForCountry(feature) {
  // d3.geo.centroid is unstable, see https://github.com/mbostock/d3/issues/1883
  var props = feature['properties'];
  var centroid;
  if (props.centroid_lat) {
    centroid = [props.centroid_lon, props.centroid_lat];
  } else {
    centroid = d3.geo.centroid(feature);
  }

  var lon = centroid[0], lat = centroid[1];
  var proj = d3.geo.albers()
    .center([0, 0])
    .rotate([-lon, -lat])
    .parallels([0, 60])
    .scale(1000)
    .translate([0,0]);
  return proj;
}

function transformForDrag(d) {
  return 'translate(' + [d.dx,d.dy] + ')';
}

function transformStatic(d) {
  var xy = [d.static_dx, d.static_dy];
  return "translate(" + xy + ")";
}

var drag = d3.behavior.drag()
  .on('drag', function(d, i) {
      d.dx += d3.event.dx;
      d.dy += d3.event.dy;
      d3.select(this)
        .attr('transform', transformForDrag);
  })
  .on('dragstart', function(d, i) {
    // TODO(danvk): look into selection.order() or selection.sort()
    d3.select(this.parentNode).moveToFront();
    d3.select(this).classed('in-transit', true);
    d3.event.sourceEvent.stopPropagation(); // silence other listeners, e.g. zoom
    d3.event.sourceEvent.preventDefault();
  })
  .on('dragend', function() {
    d3.select(this).classed('in-transit', false);
  });

var zoom = d3.behavior.zoom().on('zoom', function() {
  var sx = zoom.scale(), sy = sx, cx = width/2, cy = height/2;

  // See http://stackoverflow.com/questions/6711610/how-to-set-transform-origin-in-svg
  var matrix = [sx, 0, 0, sy, cx-sx*cx, cy-sy*cy];
  
  d3.select('.container').attr('transform', 'matrix(' + matrix + ')')
});

var geojson_features;

function getPacker() {
  var m = /pack=([a-zA-Z]+)/.exec(location.search)
  var packer;
  if (m) {
    var packerName = m[1];
    packer = {
      'overlap': overlappingPacker,
      'scootch': scootchedOverlappingPacker,
      'horizontal': horizontalPacker,
      'vertical': verticalPacker,
      'diagonal': diagonalPacker,
      'combined': combinedPacker
    }[packerName];
    if (!packer) throw "Invalid packer: " + packerName;
  } else {
    packer = combinedPacker;
  }
  return offsetPacker(insetPacker(packer, 0.1));
}

function getVisibleSvgArea() {
  var windowSize = {
    width: $(window).width(),
    height: $(window).height()
  }, panel = {
    width: $('#sidebar').width(),
    height: $('#sidebar').height()
  };
  
  var $sc = $('.size-comparison:visible');
  var comparisonBottom =
      $sc.length ? $sc.offset().top + $sc.height() : 0;

  if (panel.width / windowSize.width > panel.height / windowSize.height) {
    var t = Math.max(panel.height, comparisonBottom);
    return {
      top: t,  // comparison is below panels.
      left: 0,
      width: windowSize.width,
      height: windowSize.height - t
    };
  } else {
    return {
      top: comparisonBottom,
      left: 0,
      width: windowSize.width - panel.width,
      height: panel.height - comparisonBottom
    };
  }
}

// This is the main "display" function. It configures the projection and
// layout and creates the shapes.
function setDisplayForFeatures(features) {
  if (features.length != 2) throw "Only two shapes supported (for now!)";

  // TODO: get rid of these globals.
  width = document.getElementById('svg-container').offsetWidth;
  height = document.getElementById('svg-container').offsetHeight;
  d3.select('#svg-container svg')
      .attr('width', width)
      .attr('height', height);
  var svgArea = getVisibleSvgArea();

  var paths = features.map(function(feature) {
    var proj = projectionForCountry(feature);
    return d3.geo.path().projection(proj);
  });

  var bounds = features.map(function(d, i) { return paths[i].bounds(d); });
  var spans = boundsToSpans(bounds);
  var layout = getPacker()(svgArea, spans, features);

  paths.forEach(function(path) {
    var proj = path.projection();
    proj.scale(layout.scaleMult * proj.scale());
  });
  bounds = features.map(function(d, i) { return paths[i].bounds(d); });
  spans = boundsToSpans(bounds);

  features.forEach(function(d, i) {
    var span = spans[i];
    d.dx = 0; d.dy = 0;  // initial drag offsets
    d.static_dx = layout.offsets[i].x;
    d.static_dy = layout.offsets[i].y;
  });

  var dataEls = svg.select('.container').selectAll('.force')
    .data(features, function(f) { return f.id; });

  // enter
  var draggableG = dataEls.enter().append('g')
    .attr('class', function(d, i) { return 'force force' + i; })
      .append('g')
      .attr('class', 'draggable');

   draggableG.append('path')
      .attr('class', function(d, i) { return 'shape shape' + i; })
      .attr('d', function(d, i) { return paths[i](d); });
      
   // ... for layout debugging
   /*
   draggableG.append('rect')
      .attr('x', function(d, i) { return spans[i].centerX - spans[i].width / 2 })
      .attr('y', function(d, i) { return spans[i].centerY - spans[i].height / 2 })
      .attr('width', function(d, i) { return spans[i].width })
      .attr('height', function(d, i) { return spans[i].height; });
   draggableG.append('circle')
     .attr('cx', 0)
     .attr('cy', 0)
     .attr('r', 4);
     */

  // update
  dataEls.select('.shape')
      .attr('d', function(d, i) { return paths[i](d); });
  dataEls.attr('transform', transformStatic);

  // exit
  dataEls.exit().remove();

  if ('topShapeIndex' in layout) {
    svg.selectAll('.force' + layout.topShapeIndex).moveToFront();
  }

  svg.selectAll('.draggable').attr('transform', transformForDrag).call(drag);
  svg.call(zoom);
}

function featureForId(id) {
  for (var i = 0; i < geojson_features.length; i++) {
    var feature = geojson_features[i];
    if (feature.id == id) return feature;
  }
  return null;
}

// See http://stackoverflow.com/a/20293441/388951
function isTouch() {
  try{ document.createEvent("TouchEvent"); return true; }
  catch(e){ return false; }
}

function addChooserListeners() {
  $('select.choose').on('change', function(e) {
    var id = $(this).val();
    var ids = [$('#choose0').val(), $('#choose1').val()];
    var changedIdx = $('select.choose').index(this);
    updateEl(changedIdx, ids[changedIdx]);
    history.pushState(null, '', '/' + ids[0] + '+' + ids[1]);
    trackAnalyticsPageView();

    // forcibly dismiss keyboard on mobile.
    if (isTouch()) {
      document.activeElement.blur();
    }
  });
}

function updateEl(changedIdx, newId) {
  var otherShapeId = geojson_features[1 - changedIdx].id;
  $.get('/shape/' + newId, {
      shape_index: changedIdx,
      other_shape: otherShapeId
    })
    .success(function(data) {
      geojson_features[changedIdx] = data.feature;
      $('#side-panel' + changedIdx + ' .feature-panel').html(data.panel);
      $('.size-comparison').html(data.comparison);
      document.title = data.title;
      zoom.scale(1);
      setDisplayForFeatures(geojson_features);
    })
    .fail(function(e) {
      console.log(e);
    });
}

// Ping Google Analytics with the current URL (e.g. after history.pushState).
// See http://stackoverflow.com/a/4813223/388951
function trackAnalyticsPageView() {
  var url = location.pathname + location.search  + location.hash;
  ga('send', 'pageview', { 'page': url });
}
