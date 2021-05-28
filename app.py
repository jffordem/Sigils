from flask import Flask, render_template, request, send_from_directory
from sigils import findSolution
import os

app = Flask(__name__)

@app.route('/favicon.ico')
def favicon():
    return send_from_directory(os.path.join(app.root_path, 'static'), 'favicon.ico', mimetype='image/vnd.microsoft.icon')

@app.route('/', methods=['GET','POST'])
def index():
    if all(key in request.form for key in 'rows cols sigils timeout'.split()):
        rows = int(request.form['rows'])
        cols = int(request.form['cols'])
        sigils = request.form['sigils']
        timeout = int(request.form['timeout'])
    else:
        rows = 3
        cols = 4
        sigils = 'LJO'
        timeout = 20
    solution, message = findSolution(rows, cols, sigils, timeout)
    puzzle = { 
        'rows': rows,
        'cols': cols,
        'sigils': sigils,
        'timeout': timeout,
        'message': message,
        'solution': solution
    }
    return render_template('index.html', puzzle=puzzle)
