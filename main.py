from flask import Flask, render_template, request
import numpy
import datetime
from pymongo import MongoClient
import json

from query_data import get_dates
from query_data import get_data


app = Flask(__name__)

labels = [
    'JAN', 'FEB', 'MAR', 'APR',
    'MAY', 'JUN', 'JUL', 'AUG',
    'SEP', 'OCT', 'NOV', 'DEC'
]

# bitcoin
bitcoinValues = [
    7188.46, 9388.66, 8540.26, 6671.95, 8771.57, 9564.95, 9153.95, 11354.16, 11964.21, 10626.60, 13762.97, 18795.20]

# ether
etherValues = [186.26, 229.79, 133.76, 215.2, 243.63, 228.33, 336.21, 423.08, 357.33, 383.68, 567.68, 746.06]

# doge
dogeValues = [0.002381, 0.002216, 0.001800, 0.002460, 0.002573, 0.002314, 0.003224, 0.003210, 0.002634, 0.002568,
              0.003551, 0.004666]

cryptos = ["Bitcoin", "Ethereum", "Doge"]
crypto_values = [bitcoinValues, etherValues, dogeValues]

colors = [
    "#F7464A", "#46BFBD", "#FDB45C", "#FEDCBA",
    "#ABCDEF", "#DDDDDD", "#ABCABC", "#4169E1",
    "#C71585", "#FF4500", "#FEDCBA", "#46BFBD"]


def create_scatter_data(crypto_values):
    scatter_data = []
    for i in range(len(labels)):
        temp = [labels[i], crypto_values[i]]
        scatter_data.append(temp)
    return scatter_data


@app.route('/')
def home():
    return render_template('home.html')


@app.route('/about/')
def about():
    return render_template('about.html')


@app.route('/results/')
def results(crypto_one, crypto_two, program, startdate, enddate):
    title = crypto_one + "-" + crypto_two + " " + program + " Results"
    c1, c2 = 0, 0
    for i in range(len(cryptos)):
        if crypto_one == cryptos[i]:
            c1 = i
        if crypto_two == cryptos[i]:
            c2 = i
    correlation = round(numpy.corrcoef(crypto_values[c1], crypto_values[c2])[1, 0], 3)

    dates = get_dates(startdate, enddate)
    values1 = get_data(dates)
    # incorporate start and end date into get_dates and get_data
    # incorporate get_data into values1 and 2
    return render_template('results.html', title=title, crypto_one=crypto_one, crypto_two=crypto_two, program=program,
                           labels=labels, values1=values1, values2=crypto_values[c2],
                           scatter1=create_scatter_data(crypto_values[c1]),
                           scatter2=create_scatter_data(crypto_values[c2]), startdate=startdate, enddate=enddate,
                           correlation=correlation)


@app.route('/', methods=['POST'])
def my_form_post():
    crypto_one = request.form['crypto_name']
    crypto_two = request.form['crypto_name_2']
    program = request.form['program']
    startdate = request.form['startdate']
    enddate = request.form['enddate']
    return results(crypto_one, crypto_two, program, startdate, enddate)


if __name__ == '__main__':
    app.run(debug=True)
