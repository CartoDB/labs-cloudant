#!/usr/bin/env python
import os
import requests
from urlparse import urlparse, parse_qs
from flask import Flask, request, Response, jsonify

app = Flask(__name__)
app.debug = False


@app.route('/url-proxy/')
def index():
    geojson = {"type": 'FeatureCollection', "features": []}

    url = request.args.get("url")
    if url is None:
        return Response(status=400)

    params = parse_qs(urlparse(url).query)

    if "skip" not in params:
        params["skip"] = 0

    need_more = True

    while need_more is True:
        r = requests.get(url, params)

        if r.status_code != 200:
            return Response(status=400)

        try:
            r = r.json()
        except AttributeError:
            return Response(status=400)

        try:
            rows = r["rows"]
            total_rows = r["total_rows"]
            offset = r["offset"]
        except AttributeError:
            return Response(status=400)

        for row in rows:
            try:
                feature = row["doc"]
            except AttributeError:
                continue
            else:
                if "type" not in feature or feature["type"].lower() != "feature":
                    continue

            geojson_entry = {"type": "Feature"}

            try:
                geojson_entry["geometry"] = feature["geometry"]
            except AttributeError:
                continue

            try:
                geojson_entry["properties"] = feature["properties"]
            except AttributeError:
                pass

            geojson["features"].append(geojson_entry)

        params = parse_qs(urlparse(url).query)
        skip = offset + len(rows)
        if skip < total_rows:
            params["skip"] = offset + len(rows)
        else:
            need_more = False

    return jsonify(geojson)


app.run()
