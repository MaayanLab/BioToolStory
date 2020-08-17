import os
import json
import flask
from dotenv import load_dotenv
from flask_sqlalchemy import SQLAlchemy
from flask_caching import Cache
import requests

load_dotenv(verbose=True)

ROOT_PATH = os.environ.get('ROOT_PATH', '/biotoolstory_middleman/')
META_API = os.environ.get('META_API', 'https://maayanlab.cloud/biotoolstory/metadata-api')
BASE_URL = os.environ.get('BASE_URL', 'https://maayanlab.cloud/biotoolstory')

# Load any additional configuration parameters via
#  environment variables--`../.env` can be used
#  for sensitive information!

config = {
    "CACHE_TYPE": "simple", # Flask-Caching related configs
}


app = flask.Flask(__name__,
  static_url_path=ROOT_PATH + 'static',
  static_folder='static',
)

app.config.from_mapping(config)
cache = Cache(app)

app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('POSTGRES_URI', '')
db = SQLAlchemy(app)

@cache.cached(timeout=1000)
def get_landing_ui():
  filter_json = json.dumps({
    "where": {
        "meta.$validator": "/dcic/signature-commons-schema/v5/meta/schema/landing-ui.json"
    }
  })
  payload = { 
    "filter": filter_json
  }
  for tries in range(5):
    res = requests.get(META_API + "/schemas", params=payload)
    if res.ok:
      break
  else:
    raise Exception(res.text)
  schema = res.json()
  theme = schema[0]["meta"]["content"].get("theme_mod", {})
  favicon = schema[0]["meta"]["content"].get("favicon", {})
  background_props = schema[0]["meta"]["content"].get("background_props", {})
  font_families = schema[0]["meta"]["content"].get("font_families", {})
  header_info = schema[0]["meta"]["content"].get("header_info", {})
  return {
    "ui": {
      "theme": theme,
      "favicon": favicon,
      "background_props": background_props,
      "font_families": font_families,
      "header_info": header_info,
    }
  }

def get_schemas():
  filter_json = json.dumps({
    "where": {
        "meta.$validator": "/dcic/signature-commons-schema/v5/meta/schema/ui-schema.json"
    }
  })
  payload = { 
    "filter": filter_json
  }
  for tries in range(5):
    res = requests.get(META_API + "/schemas", params=payload)
    if res.ok:
      return [i["meta"] for i in res.json()]
  else:
    raise Exception(res.text)

@app.route(ROOT_PATH + 'static')
def staticfiles(path):
  return flask.send_from_directory('static', path)


@app.route(ROOT_PATH, methods=['GET'])
def index():
  ui = get_landing_ui()
  schemas = get_schemas()
  props = {
    **ui,
    "schemas": schemas,
    "title": "BioToolStory Middleman",
    "preferred_names": {
      "signatures": "Tools",
      "libraries": "Journals",
    }
  }
  props = json.dumps(props).replace("${PREFIX}", BASE_URL)
  return flask.render_template('index.html', props=json.loads(props))

# Add the rest of your routes....
