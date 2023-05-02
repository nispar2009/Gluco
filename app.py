from flask import Flask, render_template, request, redirect
from func import *

app = Flask(__name__)

create_data()

@app.route('/', methods=['GET', 'POST'])
def index():
    last_10_readings = py_readings()
    if request.method == 'GET':
        return render_template('index.html', last_10=last_10_readings, basal=basal_suggest())
    
    is_pred = bool(int(request.form['pred']))

    if is_pred:
        reading = int(request.form['reading2'])
        time = request.form['time2']
        food = int(request.form['food2'])

        return render_template('index.html', last_10=last_10_readings, basal=basal_suggest(), _pred=pred(reading, time, food))
    
    current = request.form['current']
    time = request.form['time']
    result = request.form['result']
    insulin = float(request.form['insulin'])
    food = int(request.form['food'])

    add_reading(time, food, current, result, insulin)

    return redirect('/')

@app.route('/purge')
def purge():
    del_data()
    return redirect('/')

if __name__ == "__main__":
    app.run()