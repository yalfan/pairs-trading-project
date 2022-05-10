import os
from flask import Flask, render_template, request, redirect, url_for
from werkzeug.utils import secure_filename

from values import *
from query_data import *
from custom_backtest import *
from importcoin import *

app = Flask(__name__)


colors = [
    "#F7464A", "#46BFBD", "#FDB45C", "#FEDCBA",
    "#ABCDEF", "#DDDDDD", "#ABCABC", "#4169E1",
    "#C71585", "#FF4500", "#FEDCBA", "#46BFBD"]

now = (datetime.datetime.today() - datetime.timedelta(days=1)).date()

@app.route('/')
def home():
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


@app.route('/backtest', methods=['GET', 'POST'])
def backtest():
    crypto_one = request.args['crypto_one']
    crypto_two = request.args['crypto_two']
    start_date = request.args['start_date']
    end_date = request.args['end_date']
    bt_params = 15, 15, 0, 2, 1, 0
    try:
        ma_period = int(request.args['ma_period'])
        std_period = int(request.args['std_period'])
        max_dur = int(request.args['max_dur'])
        entry_threshold = float(request.args['entry_threshold'])
        exit_threshold = float(request.args['exit_threshold'])
        sl_threshold = float(request.args['sl_threshold'])
        bt_params = ma_period, std_period, max_dur, entry_threshold, exit_threshold, sl_threshold
    except KeyError:
        pass
    else:
        bt_params = ma_period, std_period, max_dur, entry_threshold, exit_threshold, sl_threshold

    avg1 = get_data(start_date, end_date, crypto_one)[0]
    avg2 = get_data(start_date, end_date, crypto_two)[0]

    title = crypto_one + "-" + crypto_two + " Backtest Results"

    dates = get_dates(start_date, end_date)

    df1, df2 = get_data_dataframe(start_date, end_date, crypto_one), \
               get_data_dataframe(start_date, end_date, crypto_two)

    df1.name = crypto_one
    df2.name = crypto_two
    bt = custom_backtest(df1, df2, bt_params, 200000)
    final_df = get_trades_df(bt)
    equity = get_equity_curve(bt)
    values = get_values(start_date, end_date, 200000, final_df, equity)

    return render_template('backtest.html', title=title, crypto_one=crypto_one, crypto_two=crypto_two,
                           function="Backtest", labels=get_dates_string_daily(dates), equity=equity, values=values,
                           start_date=start_date, end_date=end_date, values1=avg1, values2=avg2,
                           tables=[final_df.to_html(classes='bt_table', header="true", col_space=100)],
                           df_rows=final_df, now=now, bt_params=bt_params)


@app.route('/analyze', methods=['GET', 'POST'])
def analyze():
    crypto_one = request.args['crypto_one']
    crypto_two = request.args['crypto_two']
    start_date = request.args['start_date']
    end_date = request.args['end_date']

    title = crypto_one + "-" + crypto_two + " Analyze Results"

    avg1 = get_data(start_date, end_date, crypto_one)[0]
    avg2 = get_data(start_date, end_date, crypto_two)[0]

    correlation = find_correlation(avg1, avg2)
    cointegration = find_cointegration(avg1, avg2)[1]
    final_df = find_best_pairs(start_date, end_date)

    dates = get_dates(start_date, end_date)
    return render_template('analyze.html', title=title, crypto_one=crypto_one, crypto_two=crypto_two, function="Analyze",
                           labels=get_dates_string_daily(dates), values1=avg1, values2=avg2,
                           correlation=correlation, cointegration=cointegration,
                           tables=[final_df.to_html(classes='a_table', header="true", index=False,
                                                    columns=['Coin1', 'Coin2', 'Correlation', 'Cointegration P-Value'])],
                           df_rows=final_df, start_date=start_date, end_date=end_date, now=now)


@app.route('/graph', methods=['GET', 'POST'])
def graph():
    crypto_one = request.args['crypto_one']
    crypto_two = request.args['crypto_two']
    start_date = request.args['start_date']
    end_date = request.args['end_date']

    title = crypto_one + "-" + crypto_two + " Graph Results"

    dates = get_dates(start_date, end_date)
    avg1 = get_data(start_date, end_date, crypto_one)[4]
    avg2 = get_data(start_date, end_date, crypto_two)[4]

    return render_template('graph.html', title=title, crypto_one=crypto_one, crypto_two=crypto_two, function="Graph",
                           labels=get_dates_string_daily(dates), values1=avg1, values2=avg2,
                           now=now, start_date=start_date, end_date=end_date)


@app.route('/handle_data', methods=['POST'])
def handle_data():
    crypto_one = request.form['crypto_one']
    crypto_two = request.form['crypto_two']
    function = request.form['function']
    start_date = request.form['start_date']
    end_date = request.form['end_date']
    """
    ma_period
    std_period
    max_dur
    entry_threshold
    exit_threshold
    sl_threshold

    Moving average period
    standard deviation period
    Maximum trading duration
    Entry threshold
    Exit threshold
    Stop/Loss threshold
    """

    return results(crypto_one, crypto_two, function, start_date, end_date)


@app.route('/upload')
def upload():
    return render_template('upload.html')


@app.route('/uploader', methods=['GET', 'POST'])
def upload_coin():
    os.makedirs(os.path.join(app.instance_path, 'uploadeddata'), exist_ok=True)
    crypto_csv_file = request.files['crypto_csv_file']
    new_crypto = request.form['new_crypto_name']
    filename = secure_filename(crypto_csv_file.filename)
    filename_path = 'instance/uploadeddata/%s.csv' % new_crypto
    crypto_csv_file.save(os.path.join(app.instance_path, 'uploadeddata', filename))
    importCoin(filename_path, new_crypto)
    print(crypto_csv_file)
    print(type(crypto_csv_file))
    return 'wozers saved file'


@app.route('/handle_backtest_data', methods=['POST'])
def handle_backtest_data():
    crypto_one = request.form['crypto_one']
    crypto_two = request.form['crypto_two']
    function = request.form['function']
    start_date = request.form['start_date']
    end_date = request.form['end_date']
    """
    ma_period=ma_period, std_period=std_period, max_dur=max_dur,
    entry_threshold=entry_threshold, exit_threshold=exit_threshold,
    sl_threshold=sl_threshold
    """
    if function == "Backtest":
        ma_period = request.form['ma_period']
        std_period = request.form['std_period']
        max_dur = request.form['max_dur']
        entry_threshold = request.form['entry_threshold']
        exit_threshold = request.form['exit_threshold']
        sl_threshold = request.form['sl_threshold']
        return redirect(url_for('backtest', crypto_one=crypto_one, crypto_two=crypto_two,
                                start_date=start_date, end_date=end_date, ma_period=ma_period, std_period=std_period,
                                max_dur=max_dur, entry_threshold=entry_threshold, exit_threshold=exit_threshold,
                                sl_threshold=sl_threshold
                                ))

    else:
        return results(crypto_one, crypto_two, function, start_date, end_date)


if __name__ == '__main__':
    app.run(debug=True)
