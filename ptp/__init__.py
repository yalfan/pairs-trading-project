from flask import Flask
import os

app = Flask(__name__)

app.secret_key = os.getenv("SECRET_KEY")

from ptp import routes
