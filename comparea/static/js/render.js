$(function() {
  $(".choose").select2();
  addChooserListeners();

  // Hide the address bar!
  setTimeout(function(){
    window.scrollTo(0, 1);
  }, 0);

  setDisplayForFeatures(geojson_features);

  $(window).on('resize', function() {
    setDisplayForFeatures(geojson_features);
  });

  // See http://stackoverflow.com/a/22590727/388951
  window.matchMedia("(orientation: portrait)").addListener(function() {
    window.scrollTo(0, 0);
  });
});
