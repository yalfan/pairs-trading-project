from flask import Flask, render_template, request
import numpy
import datetime
from pymongo import MongoClient
import json

from query_data import *

app = Flask(__name__)


colors = [
    "#F7464A", "#46BFBD", "#FDB45C", "#FEDCBA",
    "#ABCDEF", "#DDDDDD", "#ABCABC", "#4169E1",
    "#C71585", "#FF4500", "#FEDCBA", "#46BFBD"]


@app.route('/')
def home():
    return render_template('home.html', now='{d.year}-{d.month}-{d.day}'.format(d=datetime.datetime.now().date()))


@app.route('/about/')
def about():
    return render_template('about.html')


@app.route('/results/')
def results(crypto_one, crypto_two, program, startdate, enddate):
    title = crypto_one + "-" + crypto_two + " " + program + " Results"

    dates = get_dates(startdate, enddate, crypto_one)
    values1 = get_data(startdate, enddate, crypto_one)[0]
    values2 = get_data(startdate, enddate, crypto_two)[0]

    
    # avg1, open1, high1, low1, close1, volume1 = get_data(startdate, enddate, crypto_one)
    # avg2, open2, high2, low2, close2, volume2 = get_data(startdate, enddate, crypto_two)

    correlation = round(numpy.corrcoef(values1, values2)[1, 0], 3)
    #cagr1 = ((values1[0][1][0]/values1[4][0])**(1/values1[6])) - 1
    #cagr2 = ((values2[1][0]/values2[4][0])**(1/values2[6])) - 1
    #include in the below render_template: cagr1=cagr1, cagr2=cagr2

    # incorporate start and end date into get_dates and get_data DONE
    # incorporate get_data into values1 and 2 DONE
    return render_template('results.html', title=title, crypto_one=crypto_one, crypto_two=crypto_two, program=program,
                           labels=get_dates_string_daily(dates), values1=values1, values2=values2, startdate=startdate, enddate=enddate,
                           correlation=correlation, now='{d.year}-{d.month}-{d.day}'.format(d=datetime.datetime.now().date()))


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
