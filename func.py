import pyodbc

class Reading():
    def __init__(self, timing, food, present, result, insulin):
        self.timing = timing
        self.food = food
        self.present = present
        self.result = result
        self.insulin = insulin

# CREATE TABLE readings (timing TEXT, food INT, present INT, result INT, insulin FLOAT)

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

def py_readings(timing=None):
    conn = pyodbc.connect('Driver={SQL Server}; Server=NISANTH_PC\SQLEXPRESS; Database=gluco;Trusted_Connection=yes')
    cursor = conn.cursor()
    if timing:
        cursor.execute('SELECT * FROM readings WHERE timing LIKE ?', timing)
        all_readings = cursor.fetchall()
    else:
        cursor.execute('SELECT * FROM readings')
        all_readings = cursor.fetchall()
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

def pred(reading, timing, food):
    all_readings = (py_readings(timing))[-2:]
    entries = len(all_readings)

    if entries < 1:
        return 'Gluco needs at least 1 previous reading at this timing to provide suggestions.'

    suggestions = []

    for this_reading in all_readings:
        present = analyze_sugar(reading)
        analyze_then = analyze_sugar(this_reading.present)
        analyze_result = analyze_sugar(this_reading.result)

        predict = this_reading.insulin + (analyze_result / 4) + (food / 2) + ((present - analyze_then) / 4) - (this_reading.food / 2)

        suggestions.append(predict)

    return avg(suggestions)

# def pred(59, timing, 0):
#     all_readings = (py_readings(timing))[-2:]
#     entries = len(all_readings)

#     if entries < 1:
#         return 'Gluco needs at least 1 previous reading at this timing to provide suggestions.'

#     suggestions = []
    
#     for this_reading in all_readings:
#         present = analyze_sugar(59)
#         analyze_then = analyze_sugar(this_reading.present)
#         analyze_result = analyze_sugar(this_reading.result)

#         predict = this_reading.insulin + (analyze_result / 4) + (0 / 2) + ((present - analyze_then) / 4) - (this_reading.food / 2)

#         suggestions.append(predict)

#     return avg(suggestions)

def add_reading(timing, food, present, result, insulin):
    conn = pyodbc.connect('Driver={SQL Server}; Server=NISANTH_PC\SQLEXPRESS; Database=gluco;Trusted_Connection=yes')
    cursor = conn.cursor()
    cursor.execute('INSERT INTO readings (timing, food, present, result, insulin) VALUES (?, ?, ?, ?, ?)', timing, food, present, result, insulin)
    conn.commit()

def basal_suggest():
    conn = pyodbc.connect('Driver={SQL Server}; Server=NISANTH_PC\SQLEXPRESS; Database=gluco;Trusted_Connection=yes')
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