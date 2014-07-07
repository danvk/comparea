function AreaOfPolygon(points) {
  var A = 0;
  var N = points.length;
  for (var i = 0; i < N; i++) {
    var x_i = points[i][0];
    var y_i = points[i][1];
    var x_ip1 = points[(i+1) % N][0];
    var y_ip1 = points[(i+1) % N][1];
    A += (x_i * y_ip1 - x_ip1 * y_i);
  }
  return A / 2;
}

function CenterOfMassOfPolygon(points) {
  var A = AreaOfPolygon(points);
  var N = points.length;
  var cx = 0;
  var cy = 0;
  for (var i = 0; i < N; i++) {
    var x_i = points[i][0];
    var y_i = points[i][1];
    var x_ip1 = points[(i+1) % N][0];
    var y_ip1 = points[(i+1) % N][1];
    var part = (x_i * y_ip1 - x_ip1 * y_i);
    cx += ((x_i + x_ip1) * part);
    cy += ((y_i + y_ip1) * part);
  }
  return [cx/(6*A), cy/(6*A), Math.abs(A)];
}

function CenterOfMassOfShape(polygons) {
  var total_A = 0
  var total_cx = 0
  var total_cy = 0

  $.each(polygons, function(_, polygon) {
    var parts = CenterOfMassOfPolygon(polygon);
    var cx = parts[0];
    var cy = parts[1];
    var A = parts[2];
    total_cx += A * cx
    total_cy += A * cy
    total_A += A
  });

  return [total_cx / total_A, total_cy / total_A];
}
