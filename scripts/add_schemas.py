import os
import json
import requests
from requests.auth import HTTPBasicAuth
from dotenv import load_dotenv
import time
from glob import glob
from uuid import uuid4
import time
import base64

load_dotenv(dotenv_path="../.env")

APIURL = os.getenv("APIURL")
USERNAME = os.getenv("USERNAME")
PASSWORD = os.getenv("PASSWORD")

auth = HTTPBasicAuth(USERNAME,PASSWORD)
credential = base64.b64encode('{username}:{password}'.format(
    username=USERNAME, password=PASSWORD
  ).encode()).decode()

headers = {
    "Content-Type": "application/json",
    "Authorization": 'Basic {credential}'.format(credential=credential)
}

def create_schema(meta, validator):
    uid = str(uuid4())
    d = {"id": uid,
        "$validator": "/dcic/signature-commons-schema/v5/core/schema.json",
        "meta": {
            "$validator": validator
            }
        }
    for k,v in meta.items():
        d["meta"][k] = v
    return d


res = requests.get(APIURL+"/schemas")
for i in res.json():
    r = requests.delete(APIURL+"/schemas/"+i["id"], auth=auth)

with open("../schemas/landing.json") as o:
    landing = json.loads(o.read())
    landing = create_schema(landing, "/dcic/signature-commons-schema/v5/meta/schema/landing-ui.json")
    r = requests.post(APIURL+"/schemas/", auth=auth, json=landing)

for filename in glob("../schemas/ui-schemas/*.json"):
    with open(filename) as o:
        schema = json.loads(o.read())
        schema = create_schema(schema, "https://raw.githubusercontent.com/dcic/signature-commons-schema/v5/meta/schema/ui-schema.json")
        r = requests.post(APIURL+"/schemas/", auth=auth, json=schema)

with open("../schemas/counts.json") as o:
    counting_meta = json.loads(o.read())
    for i in counting_meta:
        counting_schema = create_schema(i, "/dcic/signature-commons-schema/v5/meta/schema/counting.json")
        r = requests.post(APIURL+"/schemas/", auth=auth, json=counting_schema)


res = requests.get(APIURL+"/optimize/refresh", auth=auth)
print(res.ok)

# res = requests.get(APIURL+"/optimize/status", auth=auth)
# while not res.text == "Ready":
#     time.sleep(1)
#     res = requests.get(APIURL+"/optimize/status", auth=auth)

res = requests.get(APIURL+"/summary/refresh", auth=auth)
print(res.ok)
