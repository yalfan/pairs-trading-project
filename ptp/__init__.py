from flask import Flask

app = Flask(__name__)

from ptp import routes
