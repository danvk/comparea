# Comparea: Compare the Areas of any two things

Read more about Comparea on its [about page](https://comparea.org/about).

## Development

Quickstart:

    python3 -m venv venv
    source env/bin/activate
    pip install -r requirements.txt
    pnpm install

To iterate on the UI:

    pnpm develop
    open http://localhost:5000/

(You may need to [turn off Airplay Receiver][airplay] on macOS for this to work.)

To regenerate GeoJSON:

    ./data/generate_osm_geojson.py data/osm-filtered.txt > data/osm.json
    ./data/generate_geojson.py > comparea/static/data/comparea.geo.json

To regenerate metadata:

    ./data/fetch_metadata.py > data/metadata.json
    ./data/generate_geojson.py > comparea/static/data/comparea.geo.json

To test deployment locally:

    heroku local web

To deploy:

    git push heroku master

[airplay]: https://developer.apple.com/forums/thread/682332
