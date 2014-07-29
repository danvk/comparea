QUnit.test('hello test', function(assert) {
  assert.ok(1 == '1', 'Passed!');
});

QUnit.test('comparea layout, squares', function(assert) {
  // the setup is two squares with their corners touching.
  // this layout requires no rescaling, but the shapes should be
  // repositioned.
  var svgArea = {
    width: 100,
    height: 100
  };

  var extents = [
    [[-25, -25], [25, 25]],
    [[-25, -25], [25, 25]]
  ];

  var layout = calculatePositionsAndScale(svgArea, extents);
  assert.deepEqual(layout, {
    offsets: [{x: 25, y: 25}, {x: 75, y: 75}],
    scaleMult: 1.0
  });
});

QUnit.test('comparea layout, squares with rescale', function(assert) {
  // same as the previous test, but this does require rescaling.
  var svgArea = {
    width: 200,
    height: 200
  };

  var extents = [
    [[-25, -25], [25, 25]],
    [[-25, -25], [25, 25]]
  ];

  var layout = calculatePositionsAndScale(svgArea, extents);
  assert.deepEqual(layout, {
    offsets: [{x: 50, y: 50}, {x: 150, y: 150}],
    scaleMult: 2.0
  });
});

QUnit.test('comparea layout, landscape squares', function(assert) {
  // this test features a 2:1 aspect ratio
  var svgArea = {
    width: 200,
    height: 100
  };

  var extents = [
    [[-25, -25], [25, 25]],
    [[-25, -25], [25, 25]]
  ];

  var layout = calculatePositionsAndScale(svgArea, extents);
  assert.deepEqual(layout, {
    offsets: [{x: 50, y: 25}, {x: 150, y: 75}],
    scaleMult: 1
  });
});

QUnit.test('comparea layout, portrait squares', function(assert) {
  // this test features a 1:2 aspect ratio
  var svgArea = {
    width: 100,
    height: 200
  };

  var extents = [
    [[-25, -25], [25, 25]],
    [[-25, -25], [25, 25]]
  ];

  var layout = calculatePositionsAndScale(svgArea, extents);
  assert.deepEqual(layout, {
    offsets: [{x: 25, y: 50}, {x: 75, y: 150}],
    scaleMult: 1
  });
});

QUnit.test('comparea layout, landscape squares rescale', function(assert) {
  // this test features a 2:1 aspect ratio and requires rescaling
  var svgArea = {
    width: 400,
    height: 200
  };

  var extents = [
    [[-25, -25], [25, 25]],
    [[-25, -25], [25, 25]]
  ];

  var layout = calculatePositionsAndScale(svgArea, extents);
  assert.deepEqual(layout, {
    offsets: [{x: 100, y: 50}, {x: 300, y: 150}],
    scaleMult: 2
  });
});

QUnit.test('comparea layout, landscape squares shrink', function(assert) {
  // this test features a 2:1 aspect ratio and requires scale shrinking.
  var svgArea = {
    width: 100,
    height: 50
  };

  var extents = [
    [[-25, -25], [25, 25]],
    [[-25, -25], [25, 25]]
  ];

  var layout = calculatePositionsAndScale(svgArea, extents);
  assert.deepEqual(layout, {
    offsets: [{x: 25, y: 12.5}, {x: 75, y: 37.5}],
    scaleMult: 0.5
  });
});
