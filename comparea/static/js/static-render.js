queue()
    .defer(d3.json, "data/world.json")
    .await(function(error, world) {
      geojson_features = topojson.feature(world, world.objects.countries).features;
      var name_id_pairs = features.map(function(feature) {
        return [feature.properties.name, feature.id];
      });
      name_id_pairs.sort();

      populateChoosers(name_id_pairs);
      $('#choose0 option[value=USA]').attr('selected', true);
      $('#choose1 option[value=AUS]').attr('selected', true);
      addChooserListeners();

      setDisplayForSelection();
    });
