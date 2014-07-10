$(function() {
  var getId = function(i) {
    return geojson_features[i].id;
  };
  populateChoosers(name_id_pairs);
  $('#choose0 option[value=' + getId(0) + ']').attr('selected', true);
  $('#choose1 option[value=' + getId(1) + ']').attr('selected', true);
  addChooserListeners();

  setDisplayForSelection();
});
