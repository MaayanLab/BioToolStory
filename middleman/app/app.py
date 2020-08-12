import os
import flask
from dotenv import load_dotenv
from flask_sqlalchemy import SQLAlchemy
import requests

load_dotenv(verbose=True)

ROOT_PATH = os.environ.get('ROOT_PATH', '/biotoolstory_middleman/')
# Load any additional configuration parameters via
#  environment variables--`../.env` can be used
#  for sensitive information!

app = flask.Flask(__name__,
  static_url_path=ROOT_PATH + 'static',
  static_folder='static',
)
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('POSTGRES_URI', '')
db = SQLAlchemy(app)

@app.route(ROOT_PATH + 'static')
def staticfiles(path):
  return flask.send_from_directory('static', path)

@app.route(ROOT_PATH, methods=['GET'])
def index():
    return flask.render_template('index.html')

# Add the rest of your routes....
