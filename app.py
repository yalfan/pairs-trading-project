from flask import Flask, render_template, request, redirect, url_for

from values import *
from query_data import *
from custom_backtest import *
from importcoin import *

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

    avg1 = get_data(start_date, end_date, crypto_one)[0]
    avg2 = get_data(start_date, end_date, crypto_two)[0]

    title = crypto_one + "-" + crypto_two + " Backtest Results"

    dates = get_dates(start_date, end_date, crypto_one)

    """backtest_results1, backtest_results2 = backtest_data(get_data_dataframe(start_date, end_date, crypto_one),
                                                         get_data_dataframe(start_date, end_date, crypto_two))
    trades1 = backtest_results1["_trades"].drop(columns=['EntryBar', 'ExitBar', 'ReturnPct'])
    names1 = create_names(crypto_one, len(trades1.index))
    trades1 = (pd.concat([names1, trades1], axis=1)).rename(columns={0: "Name"})

    trades2 = backtest_results2["_trades"].drop(columns=['EntryBar', 'ExitBar', 'ReturnPct'])
    names2 = create_names(crypto_two, len(trades2.index))
    trades2 = (pd.concat([names2, trades2], axis=1)).rename(columns={0: "Name"})

    final_df = combine_trades(get_trades(trades1), get_trades(trades2))

    values = get_values_pair(start_date, end_date, 200000, backtest_results1, backtest_results2)

    equity1 = backtest_results1['_equity_curve']["Equity"].tolist()
    equity2 = backtest_results2['_equity_curve']["Equity"].tolist()
    equity = [a + b for a, b in zip(equity1, equity2)]"""
    df1, df2 = get_data_dataframe(start_date, end_date, crypto_one), \
               get_data_dataframe(start_date, end_date, crypto_two)
    df1.name = crypto_one
    df2.name = crypto_two
    bt = custom_backtest(df1, df2, 200000)
    final_df = get_trades_df(bt)
    equity = get_equity_curve(bt)
    values = get_values(start_date, end_date, 200000, final_df, equity)

    return render_template('backtest_pair.html', title=title, crypto_one=crypto_one, crypto_two=crypto_two,
                           function="Backtest", labels=get_dates_string_daily(dates), equity=equity, values=values,
                           start_date=start_date, end_date=end_date, values1=avg1, values2=avg2,
                           tables=[final_df.to_html(classes='data', header="true")])


@app.route('/analyze')
def analyze():
    crypto_one = request.args['crypto_one']
    crypto_two = request.args['crypto_two']
    start_date = request.args['start_date']
    end_date = request.args['end_date']

    title = crypto_one + "-" + crypto_two + " Analyze Results"

    avg1 = get_data(start_date, end_date, crypto_one)[0]
    avg2 = get_data(start_date, end_date, crypto_two)[0]

    correlation = find_correlation(avg1, avg2)
    # but there is a problem with correlation
    # for example, if you had these two lines, you could argue that they are correlated as they are both are moving in a positive direction.
    # but in pairs trading, a good pair will have the price of each currency move together, so when one does diverge, there is a high chance of them reconverging
    # so, it's important to find the cointegration of both pairs. what cointegration expresses is the extent to which the distance between the two currencies will remain constant over time
    # cointegration or something
    cointegration = find_cointegration(avg1, avg2)[1]
    final_df = find_best_pairs(start_date, end_date)

    dates = get_dates(start_date, end_date, crypto_one)
    return render_template('analyze.html', title=title, crypto_one=crypto_one, crypto_two=crypto_two, function="Analyze",
                           labels=get_dates_string_daily(dates), values1=avg1, values2=avg2,
                           correlation=correlation, cointegration=cointegration,
                           tables=[final_df.to_html(classes='data', header="true")])


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




@app.route('/upload/')
def upload():
    return render_template('upload.html')

@app.route('/fileupload')
def fileUpload(crypto_csv_file, data_base_name, new_crypto):
    importCoin(crypto_csv_file, new_crypto, new_crypto, db_url='localhost', db_port=27000)

@app.route('/', methods=['POST'])
def my_form_post():
    crypto_one = request.form['crypto_name']
    crypto_two = request.form['crypto_name_2']
    function = request.form['function']
    start_date = request.form['startdate']
    end_date = request.form['enddate']

    return results(crypto_one, crypto_two, function, start_date, end_date)

@app.route('/', methods=['UPLOAD'])
def uploadCoin():
    new_crypto = request.form['new_crypto_name']
    crypto_csv_file = request.form['crypto_csv_file']
    return fileUpload(new_crypto, crypto_csv_file)

if __name__ == '__main__':
    app.run(debug=True)

