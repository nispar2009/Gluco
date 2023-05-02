import sqlite3

class Reading():
    def __init__(self, time, food, current, result, insulin):
        self.time = time
        self.food = food
        self.current = current
        self.result = result
        self.insulin = insulin

def create_data():
    conn = sqlite3.connect('gluco.db')
    cursor = conn.cursor()
    cursor.execute('CREATE TABLE IF NOT EXISTS readings (time TEXT, food INT, current INT, result INT, insulin FLOAT)')
    conn.commit()

def calc_diff(diff):
    points = diff // 15
    if diff % 15 > 9:
        points += 1

    return points

def analyze_sugar(reading):
    if reading >= 65 and reading <= 120:
        diff = 0
    elif reading < 65:
        diff = 65 - reading
        diff = -(calc_diff(diff))
    else:
        diff = reading - 120
        diff = calc_diff(diff)
    
    return diff

def py_readings(time=None):
    conn = sqlite3.connect('gluco.db')
    cursor = conn.cursor()
    if time:
        all_readings = list(cursor.execute('SELECT * FROM readings WHERE time = ?', (time,)))
    else:
        all_readings = list(cursor.execute('SELECT * FROM readings'))
    all_readings2 = []

    for iterator in all_readings:
        reading = Reading(iterator[0], iterator[1], iterator[2], iterator[3], iterator[4])
        all_readings2.append(reading)

    return all_readings2

def avg(_list):
    counter = 0
    for iterator in _list:
        counter += iterator
    
    _avg = counter / len(_list)
    return _avg

def pred(reading, time, food):
    all_readings = (py_readings(time))[-3:]
    entries = len(all_readings)

    if entries < 1:
        return 'Gluco needs at least 1 previous reading at this time to provide suggestions.'
    
    suggestions = []
    
    for this_reading in all_readings:
        analyze_current = analyze_sugar(reading)
        analyze_then = analyze_sugar(this_reading.current)
        analyze_result = analyze_sugar(this_reading.result)

        suggestions.append(this_reading.insulin + (analyze_result / 4) - (this_reading.food / 2) + (food / 2) + ((analyze_current - analyze_then) / 4) - (this_reading.food / 2))

    return avg(suggestions)

def add_reading(time, food, current, result, insulin):
    conn = sqlite3.connect('gluco.db')
    cursor = conn.cursor()
    cursor.execute('INSERT INTO readings (time, food, current, result, insulin) VALUES (?, ?, ?, ?, ?)', (time, food, current, result, insulin))
    conn.commit()

def del_data():
    conn = sqlite3.connect('gluco.db')
    cursor = conn.cursor()
    cursor.execute('DELETE FROM readings')
    conn.commit()

def basal_suggest():
    conn = sqlite3.connect('gluco.db')
    cursor = conn.cursor()
    if len(py_readings()) > 14:
        last_15_days = (py_readings())[-15:]
        last_15_results = []
        counter = 0

        for item in last_15_days:
            last_15_results.append(item.result)
        
        for item in last_15_results:
            if analyze_sugar(item) > 0:
                counter += 1

        if counter >= 10:
            return 'Suggesting increase in basal.'
        
        counter = 0

        for item in last_15_results:
            if analyze_sugar(item) < 0:
                counter += 1

        if counter <= -10:
            return 'Suggesting decrease in basal.'
        
        return 'Basal is optimal.'
    
    return 'Insufficient readings to suggest basal.'