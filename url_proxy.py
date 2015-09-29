#!/usr/bin/env python
import requests
from flask import Flask, request, Response, jsonify

app = Flask(__name__)
app.debug = True


@app.route('/url-proxy/')
def index():
    geojson = {"type": 'FeatureCollection', "features": []}

    url = request.args.get("url")

    if url is None:
        return Response(status=400)

    first = requests.get(url)

    if first.status_code != 200:
        return Response(status=400)

    tmp_geojson = first.json()

    bookmark = None
    while tmp_geojson:
        print tmp_geojson
        try:
            bookmark = bookmark or tmp_geojson["bookmark"]
        except KeyError:
            bookmark = None
        else:
            del tmp_geojson["bookmark"]

        if len(tmp_geojson["features"]) > 0:
            geojson["features"] += tmp_geojson["features"]

            if bookmark:
                next = requests.get("%s&bookmark=%s" % (url, bookmark))
                if next.status_code != 200:
                    return Response(status=400)
                tmp_geojson = next.json()
            else:
                tmp_geojson = None
        else:
            tmp_geojson = None

    return jsonify(geojson)


app.run()
