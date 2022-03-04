from flask import Flask, render_template, request, redirect, url_for
import numpy
import datetime
from pymongo import MongoClient
import json

from values import *
from query_data import *
from backtest_data import *

app = Flask(__name__)


colors = [
    "#F7464A", "#46BFBD", "#FDB45C", "#FEDCBA",
    "#ABCDEF", "#DDDDDD", "#ABCABC", "#4169E1",
    "#C71585", "#FF4500", "#FEDCBA", "#46BFBD"]


@app.route('/')
def home():
    now = datetime.datetime.now().date()
    return render_template('home.html', now=now)


@app.route('/about/')
def about():
    return render_template('about.html')


@app.route('/results')
def results(crypto_one, crypto_two, function, start_date, end_date):
    if function == "Backtest":
        return redirect(url_for('backtest', crypto_one=crypto_one, crypto_two=crypto_two, start_date=start_date, end_date=end_date))
    elif function == "Analyze":
        return redirect(url_for('analyze', crypto_one=crypto_one, crypto_two=crypto_two, start_date=start_date, end_date=end_date))
    elif function == "Graph":
        return redirect(url_for('graph', crypto_one=crypto_one, crypto_two=crypto_two, start_date=start_date, end_date=end_date))

    # incorporate start and end date into get_dates and get_data DONE
    # incorporate get_data into values1 and 2 DONE


@app.route('/backtest')
def backtest():
    crypto_one = request.args['crypto_one']
    crypto_two = request.args['crypto_two']
    start_date = request.args['start_date']
    end_date = request.args['end_date']

    title = crypto_one + "-" + crypto_two + " Backtest Results"

    dates = get_dates(start_date, end_date, crypto_one)

    backtest_results1, backtest_results2 = backtest_data(get_data_dataframe(start_date, end_date, crypto_one),
                                                         get_data_dataframe(start_date, end_date, crypto_two))
    trades1 = backtest_results1["_trades"].drop(columns=['EntryBar', 'ExitBar', 'ReturnPct'])
    names1 = create_names(crypto_one, len(trades1.index))
    trades1 = pd.concat([names1, trades1], axis=1)
    trades1 = trades1.rename(columns={0: "Name"})

    trades2 = backtest_results2["_trades"].drop(columns=['EntryBar', 'ExitBar', 'ReturnPct'])
    names2 = create_names(crypto_two, len(trades2.index))
    trades2 = pd.concat([names2, trades2], axis=1)
    trades2 = trades2.rename(columns={0: "Name"})

    final_df = combine_trades(get_trades(trades1), get_trades(trades2))

    values = get_values_pair(start_date, end_date, 100000, backtest_results1, backtest_results2)

    equity1 = backtest_results1['_equity_curve']["Equity"].tolist()
    equity2 = backtest_results2['_equity_curve']["Equity"].tolist()
    equity = equity1 + equity2

    return render_template('backtest_pair.html', title=title, crypto_one=crypto_one, crypto_two=crypto_two,
                           function="Backtest", labels=get_dates_string_daily(dates), equity1=equity1,
                           equity2=equity2, equity=equity, values=values,
                           start_date=start_date, end_date=end_date,
                           tables=[final_df.to_html(classes='data', header="true")])


@app.route('/analyze')
def analyze():
    crypto_one = request.args['crypto_one']
    crypto_two = request.args['crypto_two']
    start_date = request.args['start_date']
    end_date = request.args['end_date']

    title = crypto_one + "-" + crypto_two + " Analyze Results"

    # avg1, open1, high1, low1, close1, volume1 = get_data(start_date, end_date, crypto_one)
    # avg2, open2, high2, low2, close2, volume2 = get_data(start_date, end_date, crypto_two)

    # correlation = round(numpy.corrcoef(values1, values2)[1, 0], 3)

    dates = get_dates(start_date, end_date, crypto_one)
    avg1 = get_data(start_date, end_date, crypto_one)[0]
    avg2 = get_data(start_date, end_date, crypto_two)[0]
    return render_template('analyze.html', title=title, crypto_one=crypto_one, crypto_two=crypto_two, function="Analyze",
                           labels=get_dates_string_daily(dates), values1=avg1, values2=avg2,)


@app.route('/graph')
def graph():
    crypto_one = request.args['crypto_one']
    crypto_two = request.args['crypto_two']
    start_date = request.args['start_date']
    end_date = request.args['end_date']

    title = crypto_one + "-" + crypto_two + " Graph Results"

    dates = get_dates(start_date, end_date, crypto_one)
    avg1 = get_data(start_date, end_date, crypto_one)[0]
    avg2 = get_data(start_date, end_date, crypto_two)[0]
    return render_template('graph.html', title=title, crypto_one=crypto_one, crypto_two=crypto_two, function="Graph",
                           labels=get_dates_string_daily(dates), values1=avg1, values2=avg2)


@app.route('/', methods=['POST'])
def my_form_post():
    crypto_one = request.form['crypto_name']
    crypto_two = request.form['crypto_name_2']
    function = request.form['function']
    start_date = request.form['startdate']
    end_date = request.form['enddate']
    return results(crypto_one, crypto_two, function, start_date, end_date)


if __name__ == '__main__':
    app.run(debug=True)
