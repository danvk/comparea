$(function() {
  var getId = function(i) {
    return geojson_features[i].id;
  };
  populateChoosers(name_id_pairs);
  $('#choose0 option[value=' + getId(0) + ']').attr('selected', true);
  $('#choose1 option[value=' + getId(1) + ']').attr('selected', true);
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
