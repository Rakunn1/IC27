from flask import Flask, render_template, jsonify, request
import pandas as pd
import numpy as np
import io
import base64
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import IC27_etl as etl
from datetime import datetime, timedelta

app = Flask(__name__)


def prediction_model():
    # returns arguments utilized in plot (dates, delays, linear_regression)
    # and expected_diff for next period [sec]
    dates_lst, delays = etl.fetch_prediction_data()

    dates = np.arange(1, len(dates_lst) + 1)
    delays = np.array(delays)

    '''
    if len(delays)>0:
        dates = np.arange(1, len(dates_lst)+1)
        delays = np.array(delays)
    else:
        dates = np.arange(1, 2)
        delays = np.array([1])
    '''

    coeffs = np.polyfit(dates, delays, 1)
    linear_regression = np.polyval(coeffs, dates)

    a, b = coeffs
    expected_diff = round((a*(len(dates_lst)+1) + b))

    return dates, delays, linear_regression, expected_diff


def generate_plot():
    dates, delays, linear_regression = (prediction_model()[n] for n in range(3))

    plt.figure(figsize=(10, 5))
    plt.plot(dates, delays, label='delays', marker='o')
    plt.plot(dates, linear_regression, label='regression curve', linestyle='--')
    plt.xlabel('Thursdays')
    plt.ylabel('Delays [sec]')
    plt.title('IC27 delays vs prediction')
    plt.legend()

    img = io.BytesIO()
    plt.savefig(img, format='png')
    img.seek(0)
    plt.close()

    plot_url = base64.b64encode(img.getvalue()).decode()
    return plot_url


@app.route('/', methods=['GET'])
def index():
    plot_url = generate_plot()
    return render_template('index.html', plot_url=plot_url)


@app.route('/predict', methods=['GET'])
def predict_route():
    # route for solving Jaana's problem and printing output
    next_thursday = (datetime.now() + timedelta((3 - datetime.now().weekday()) % 7 + 4))

    expected_diff = prediction_model()[-1]

    scheduled_time_datetime = etl.fetch_scheduled_time(next_thursday)
    eta_time_datetime = scheduled_time_datetime.replace(tzinfo=None)  + timedelta(seconds=expected_diff)
    four_fifteen = datetime.combine(eta_time_datetime.date(), datetime(2000, 1, 1, 16, 15).time())
    arrivment_ind = (four_fifteen - eta_time_datetime) > timedelta(minutes=15)

    scheduledDate = scheduled_time_datetime.strftime('%Y-%m-%d')
    scheduledTime = scheduled_time_datetime.strftime('%H:%M:%S')
    eta = eta_time_datetime.strftime('%H:%M:%S')

    def generate():
        yield f'data: Predicting arrival time of train IC27 at Tampere for {scheduledDate}\n\n'
        yield f'data: Scheduled Time: {scheduledTime}\n\n'
        yield f'data: ETA: {eta}\n\n'
        yield f'data: Will Jaana arrive at time: {arrivment_ind}\n\n'
    return app.response_class(generate(), mimetype='text/event-stream')


@app.route('/generate-plot')
def generate_plot_route():
    plot_img = generate_plot()
    return plot_img


@app.route('/fetch-period', methods=['POST', 'GET'])
def fetch_period():
    start_date = request.form.get('start_date')
    end_date = request.form.get('end_date')
    result = etl.wfl_fetch_period(start_date, end_date)

    return app.response_class(result, mimetype='text/event-stream')


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)