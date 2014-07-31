$(function() {
  $(".choose").select2();
  addChooserListeners();

  // Hide the address bar!
  setTimeout(function(){
    window.scrollTo(0, 1);
  }, 0);

  setDisplayForFeatures(geojson_features);

  $(window).on('resize', function() {
    width = document.getElementById('svg-container').offsetWidth;
    height = document.getElementById('svg-container').offsetHeight;
    d3.select('#svg-container svg')
        .attr('width', width)
        .attr('height', height);

    setDisplayForFeatures(geojson_features);
  });
});
