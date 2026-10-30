from flask import Flask, render_template, request
from waitress import serve

app = Flask(__name__)

@app.route('/')
@app.route('/index')
def index():
    return render_template('index.html')

def start():
    serve(app, host="192.168.100.110", port=8000)