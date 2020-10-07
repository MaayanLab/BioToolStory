import os
import json
import flask
from dotenv import load_dotenv
from flask_sqlalchemy import SQLAlchemy
from flask_caching import Cache
import requests
from .models import Library, Signature
from .tempmodels import TempLibrary, TempSignature
from .validate import initialize_resolver, validate_entry
from flask_basicauth import BasicAuth

load_dotenv(verbose=True)

temp_model_maper = {
  "libraries": TempLibrary,
  "signatures": TempSignature
}

model_maper = {
  "libraries": Library,
  "signatures": Signature
}

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

app.config['BASIC_AUTH_USERNAME'] = os.environ['USERNAME']
app.config['BASIC_AUTH_PASSWORD'] = os.environ['PASSWORD']
app.config['BASIC_AUTH_FORCE'] = True

app.config.from_mapping(config)
cache = Cache(app)

app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('POSTGRES_URI', '')
db = SQLAlchemy(app, engine_options={"pool_pre_ping": True})

basic_auth = BasicAuth(app)

resolver = initialize_resolver()

@cache.cached(timeout=1000, key_prefix='landing')
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

@cache.cached(timeout=1000, key_prefix='schemas')
def get_schemas():
  filter_json = json.dumps({
    "where": {
        'meta.$validator': {
            "like": '%/meta/schema/ui-schema.json%'
          }
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

# input ?validator=<url>
@app.route(ROOT_PATH + "api/get_validator", methods=['GET', 'POST'])
def get_validator():
  if flask.request.method == 'GET':
    v=flask.request.args.get('validator',{})
  elif flask.request.method=='POST':
    v=flask.request.form.get('validator', {})
  try:
    if type(v) == str:
      v = json.loads(v)
    validator = v.get('url')
    res = requests.get(validator)
    if res.ok:
      return flask.jsonify(res.json())
    else:
      response = flask.jsonify({
        "error": {
          "status_code": res.status_code,
          "message": res.text
        } 
      })
      return response
  except Exception as e:
    response = flask.jsonify({
        "error": {
          "message": str(e)
        } 
      })
    return response

# filter only accepts skip and limit for now
@app.route(ROOT_PATH + "api/<table>", methods=['GET', 'POST'])
def query(table):
  if flask.request.method == 'GET':
    filters=flask.request.args.get('filter',{})
  elif flask.request.method=='POST':
    filters=flask.request.form.get('filter', {})
  if type(filters)==str:
    filters = json.loads(filters)
  limit = filters.get("limit", 10)
  skip = filters.get("skip", 0)
  model = temp_model_maper[table]
  start = skip
  end = skip+limit
  count = model.query.count()
  query = model.query.order_by(model.id)
  results = [i.serialize for i in query.offset(skip).limit(limit).all()]
  contentRange = "%d-%d/%d"%(start,end,count)
  resp = flask.jsonify(results)
  resp.headers["Content-Range"] = contentRange
  return resp

@app.route(ROOT_PATH + "api/<table>/<uid>", methods=['GET'])
def get_entry(table, uid):
  model = temp_model_maper[table]
  db_entry = model.query.filter_by(id=uid).first()
  if db_entry:
    return flask.jsonify(db_entry.serialize)
  else:
    return flask.jsonify({"error": "Not found"}), 404


@app.route(ROOT_PATH + "api/<table>/<uid>", methods=['DELETE'])
def delete_entry(table, uid):
  session = db.create_scoped_session()
  model = temp_model_maper[table]
  db_entry = session.query(model).filter_by(id=uid).first()
  if db_entry:
    try:
      session.delete(db_entry)
      session.commit()
      session.close()
      return ('', 200)
    except Exception as e:
      session.rollback()
      session.close()
      return flask.jsonify({"error": str(e)}), 400
  else:
    session.close()


@app.route(ROOT_PATH + "api/<table>/<uid>", methods=['POST', 'PATCH'])
@basic_auth.required
def patch_or_create(table, uid):
  session = db.create_scoped_session()
  model = temp_model_maper[table]
  db_entry = session.query(model).filter_by(id=uid).first()
  entry=flask.request.json
  error = validate_entry(entry, resolver)
  if not error:
    try:
      if db_entry == None and flask.request.method=='POST':
        db_entry = model(entry)
        session.add(db_entry)
        session.commit()
        session.close()
      elif not db_entry == None and flask.request.method=='PATCH':
        db_entry.update(entry)
        session.commit()
        session.close()
      else:
        session.close()
        return flask.jsonify({"error": "Invalid method %s, check if entry exists. Use POST for new entries and PATCH for existing ones"%flask.request.method}), 400
      return ('', 200)
    except Exception as e:
      session.rollback()
      session.close()
      return flask.jsonify({"error": str(e)}), 400
  else:
    session.close()
    return flask.jsonify(json.loads(error)), 406


@app.route(ROOT_PATH + "api/approve/<table>/<uid>", methods=['POST'])
@basic_auth.required
def approve_tool(table, uid):
  session = db.create_scoped_session()

  try:
    temp_model = temp_model_maper[table]
    temp_entry = session.query(temp_model).filter_by(id=uid).first()
    if not temp_entry:
      return flask.jsonify({"error": "%s does not exist"%uid}), 400
    serialized = temp_entry.serialize
    # permanent
    model = model_maper[table]
    entry = session.query(model).filter_by(uuid=uid).first()
    if entry:
      # update existing
      entry.update(serialized)
    else:
      db_entry = model(serialized)
      session.add(db_entry)
    session.delete(temp_entry)
    session.commit()
    session.close()
    return ('', 200)
  except Exception as e:
    session.rollback()
    session.close()
    return flask.jsonify({"error": str(e)}), 400
