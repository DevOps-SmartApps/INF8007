#!/usr/bin/env python3.5
import os
import td2
from flask import Flask , render_template, request, url_for, jsonify
# flask jsonify

app = Flask(__name__)

def shutdown_server():
    func = request.environ.get('werkzeug.server.shutdown')
    if func is None:
        raise RuntimeError('Not running with the Werkzeug Server')
    func()

@app.route('/')
def index():
    return render_template('td3.html')

@app.route('/courses/<course_code>')
def course(course_code):
    return jsonify(td2.request(course_code))

@app.route('/recom/<recom_code>')
def rec(recom_code):
    n = request.args["n"]
    return jsonify(td2.recom(recom_code,n))

@app.route('/analyz/<analyz_code>')
def analyze(analyz_code):
    return jsonify(td2.analyze(analyz_code))

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
