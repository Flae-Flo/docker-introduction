from flask import Flask, render_template, request
from datetime import datetime, timedelta

app = Flask(__name__)

# Tarifs pour HNO par minute
HNO_RATES = {
    'weeknight': 61.31 / 60,
    'saturday': 61.31 / 60,
    'sunday': 73.57 / 60,
    'may_1': 98.73 / 60
}

# Tarifs pour Astreinte par jour
ASTREINTE_RATES = {
    'weeknight': 35.07,
    'saturday': 44.63,
    'sunday': 57.38,
    'may_1': 57.38
}

def calculate_hno(hours, minutes, day_type):
    total_minutes = hours * 60 + minutes
    return round(total_minutes * HNO_RATES[day_type], 2)

def calculate_astreinte(start_date, start_time, end_date, end_time):
    start = datetime.combine(datetime.strptime(start_date, '%Y-%m-%d'), datetime.strptime(start_time, '%H:%M').time())
    end = datetime.combine(datetime.strptime(end_date, '%Y-%m-%d'), datetime.strptime(end_time, '%H:%M').time())
    total_amount = 0.0

    current = start
    while current < end:
        if current.weekday() == 5:  # Saturday
            rate = ASTREINTE_RATES['saturday']
        elif current.weekday() == 6:  # Sunday
            rate = ASTREINTE_RATES['sunday']
        elif current.date() == datetime.strptime('1-05', '%d-%m').date():  # 1st May
            rate = ASTREINTE_RATES['may_1']
        else:  # Weeknight
            rate = ASTREINTE_RATES['weeknight']

        total_amount += rate
        current += timedelta(days=1)

    return round(total_amount, 2)

@app.route('/', methods=['GET', 'POST'])
def index():
    result = None
    if request.method == 'POST':
        service_type = request.form.get('service_type')
        
        if service_type == 'hno':
            hours = int(request.form.get('hours'))
            minutes = int(request.form.get('minutes'))
            day_type = request.form.get('day_type')
            result = calculate_hno(hours, minutes, day_type)
        
        elif service_type == 'astreinte':
            start_date = request.form.get('start_date')
            start_time = request.form.get('start_time')
            end_date = request.form.get('end_date')
            end_time = request.form.get('end_time')
            result = calculate_astreinte(start_date, start_time, end_date, end_time)
    
    return render_template('index.html', result=result)

if __name__ == '__main__':
    app.run(debug=True)
