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

// Determine a scaling factor which will make both shapes fit on screen.
// This uses the initial scale of 1000 as a guess, then adjusts to fit.
function setScalingFactor(features, paths) {
  var bounds = features.map(function(d, i) { return paths[i].bounds(d); });
  var curWidth = 0, curHeight = 0;
  bounds.forEach(function(b) {
    curWidth += (b[1][0] - b[0][0])
    curHeight = Math.max(curHeight, b[1][1] - b[0][1]);
  });

  var horizScale = curWidth / (0.7 * width);
  var vertScale = curHeight / (0.7 * height);

  var scaleAdjustment = 1.0 / Math.max(horizScale, vertScale);
  paths.forEach(function(path) {
    var proj = path.projection();
    proj.scale(scaleAdjustment * proj.scale());
  });
}

function projectionForCountry(feature) {
  var centroid = d3.geo.centroid(feature);
  var lon = centroid[0], lat = centroid[1];
  var proj = d3.geo.albers()
    .center([0, 0])
    .rotate([-lon, -lat])
    .parallels([0, 60])
    .scale(1000)
    .translate([width / 2, height / 2]);
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
  });

var zoom = d3.behavior.zoom().on('zoom', function() {
  var sx = zoom.scale(), sy = sx, cx = width/2, cy = height/2;

  // See http://stackoverflow.com/questions/6711610/how-to-set-transform-origin-in-svg
  var matrix = [sx, 0, 0, sy, cx-sx*cx, cy-sy*cy];
  
  d3.select('.container').attr('transform', 'matrix(' + matrix + ')')
});

var geojson_features;

function setDisplayForFeatures(features) {
  if (features.length != 2) throw "Only two shapes supported (for now!)";
  if (features[0] == null || features[1] == null) return;

  var paths = features.map(function(feature) {
    var proj = projectionForCountry(feature);
    return d3.geo.path().projection(proj);
  });
  setScalingFactor(features, paths);

  var bounds = features.map(function(d, i) {
    return paths[i].bounds(d);
  });
  var xSpans = bounds.map(function(b) {
    var tl = b[0], br = b[1];
    return br[0] - tl[0];
  });

  var gapBetweenShapes = 10;
  features.forEach(function(d, i) {
    d.dx = 0; d.dy = 0;  // initial drag offsets

    var bounds = paths[i].bounds(d);

    if (i == 0) {
      // shift so that the right edge is at the center
      d.static_dx = -(bounds[1][0] - width/2);
      d.static_dx -= gapBetweenShapes / 2;
    } else {
      // shift so that the left edge is at the center
      d.static_dx = +(width/2 - bounds[0][0]);
      d.static_dx += gapBetweenShapes / 2;
    }

    d.static_dy = 0;
  });

  var dataEls = svg.select('.container').selectAll('.force')
    .data(features, function(f) { return f.id; });

  // enter
  dataEls.enter().append('g')
    .attr('class', 'force')
    .attr('transform', transformStatic)
      .append('g')
      .attr('class', 'draggable').append('path')
      .attr('class', function(d, i) { return 'shape shape' + i; })
      .attr('d', function(d, i) { return paths[i](d); });

  // update
  dataEls.select('.shape')
      .attr('d', function(d, i) { return paths[i](d); });

  // exit
  dataEls.exit().remove();

  svg.selectAll('.draggable').attr('transform', transformForDrag).call(drag);
  svg.call(zoom);
}

function setDisplayForSelection() {
  var feature0 = featureForId($('#choose0').val()),
      feature1 = featureForId($('#choose1').val());
  setDisplayForFeatures([feature0, feature1]);
}

function featureForId(id) {
  for (var i = 0; i < geojson_features.length; i++) {
    var feature = geojson_features[i];
    if (feature.id == id) return feature;
  }
  return null;
}

function addChooserListeners() {
  $('.choose').on('change', function(e) {
    var id = $(this).val();
    var ids = [$('#choose0').val(), $('#choose1').val()];
    var changedIdx = $('.choose').index(this);
    updateEl(changedIdx, ids[changedIdx]);
    history.pushState(null, '', '/' + ids[0] + '+' + ids[1]);
  });
}

function populateChoosers(name_id_pairs) {
  name_id_pairs.forEach(function(pair) {
    var name = pair[0];
    var id = pair[1];
    $('.choose').append($('<option>').attr('value', id).text(name));
  });
}

function updateEl(changedIdx, newId) {
  $.get('/shape/' + newId)
    .success(function(data) {
      geojson_features[changedIdx] = data.feature;
      $('#side-panel' + changedIdx + ' .feature-panel').html(data.panel);
      setDisplayForFeatures(geojson_features);
    })
    .fail(function(e) {
      console.log(e);
    });
}
