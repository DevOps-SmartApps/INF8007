#!/usr/bin/env python3.5
import os
from flask import Flask , render_template, request

app = Flask(__name__)

def shutdown_server():
    func = request.environ.get('werkzeug.server.shutdown')
    if func is None:
        raise RuntimeError('Not running with the Werkzeug Server')
    func()

@app.route('/shutdown', methods=['POST'])
def shutdown():
    shutdown_server()
    return 'Server shutting down...'

@app.route('/')
def index():
    return render_template('td3.html')



if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
