"""
Routes and views for the flask application.
"""

from datetime import datetime
import json

from flask import render_template, request, jsonify

from wcm_wahlergebnisse import app

@app.route('/')
@app.route('/home')
def home():
    """Renders the home page."""
    with open("../Datasets/Combined/btw_2017.geojson", "r") as fp:
        data = json.load(fp)
    return render_template(
        'index.html',
        title='election_viz',
        year=datetime.now().year,
        wahlkreise=data
    )
@app.route("/data")
def data():
    """
    request data:
        query params: type = any of btw, ew, ltw, kw
                      year = any year

        responses:
            200 --> data
            400 --> combination of type and data not found
    """
    type = request.args.get("type", type=str)  # any of btw, ew, ltw, kw
    year = request.args.get("year", type=str)
    try:
        filepath = "../Datasets/Combined/" + type + "_" + str(year) + ".geojson"
        print(filepath)
        with open(filepath, "r") as fp:
            data = json.load(fp)
    except OSError:
        return jsonify({"reason": "data_not_found"}), 400

    return jsonify(data), 200


@app.route('/contact')
def contact():
    """Renders the contact page."""
    return render_template(
        'contact.html',
        title='Contact',
        year=datetime.now().year,
        message='feel free to contact anyone of the developers for questions.'
    )

@app.route('/about')
def about():
    """Renders the about page."""
    return render_template(
        'about.html',
        title='About',
        year=datetime.now().year,
        message='Your application description page.'
    )
