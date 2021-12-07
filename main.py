from flask import Flask, render_template, request
import json
app = Flask(__name__)



labels = [
    'JAN', 'FEB', 'MAR', 'APR',
    'MAY', 'JUN', 'JUL', 'AUG',
    'SEP', 'OCT', 'NOV', 'DEC'
]

#bitcoin
bitcoinValues = [
    7188.46, 9388.66, 8540.26, 6671.95, 8771.57, 9564.95, 9153.95, 11354.16, 11964.21, 10626.60, 13762.97, 18795.20]


#ether
etherValues = [186.26, 229.79, 133.76, 215.2, 243.63, 228.33, 336.21, 423.08, 357.33, 383.68, 567.68, 746.06]

#doge
dogeValues = [186.26, 229.79, 133.76, 215.2, 243.63, 228.33, 336.21, 423.08, 357.33, 383.68, 567.68, 746.06]

cryptos = ["Bitcoin", "Ethereum", "Doge"]
cryptoValues = [bitcoinValues, etherValues, dogeValues]

colors = [
    "#F7464A", "#46BFBD", "#FDB45C", "#FEDCBA",
    "#ABCDEF", "#DDDDDD", "#ABCABC", "#4169E1",
    "#C71585", "#FF4500", "#FEDCBA", "#46BFBD"]

@app.route('/')
def home():
    return render_template('home.html')
@app.route('/about/')
def about():
    return render_template('about.html')
@app.route('/results/')
def results(crypto_one, crypto_two, program):
    title = crypto_one + "-" + crypto_two + " " + program + " Results"
    c1, c2 = 0, 0
    print(crypto_one, " ", crypto_two)
    for i in range(len(cryptos)):
        print(cryptos[i])
        if crypto_one == cryptos[i]:
            c1 = i
        if crypto_two == cryptos[i]:
            c2 = i
    print(c1, " ", c2)
    return render_template('results.html', title=title, crypto_one=crypto_one, crypto_two=crypto_two, program=program,
                           labels=labels, values1=cryptoValues[c1], values2=cryptoValues[c2])

@app.route('/', methods=['POST'])
def my_form_post():
    crypto_one = request.form['crypto_name']
    crypto_two = request.form['crypto_name_2']
    program = request.form['program']
    return results(crypto_one, crypto_two, program)

if __name__ == '__main__':
    app.run(debug=True)

