$(function() {
  addChooserListeners();

  setDisplayForFeatures(geojson_features);

  $(window).on('resize', function() {
    var width = document.getElementById('svg-container').offsetWidth,
        height = document.getElementById('svg-container').offsetHeight;
    d3.select('#svg-container svg')
        .attr('width', width)
        .attr('height', height);

  });
});
