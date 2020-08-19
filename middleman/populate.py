import os
import requests
import json
from dotenv import load_dotenv

load_dotenv(verbose=True)
META_API = os.environ.get('META_API')

res = requests.get(META_API + "/signatures", params={"filter":json.dumps({"limit": 10})})
if not res.ok:
    raise Exception(res.text)
signatures = res.json()
libids = [f["library"] for f in signatures]

filters = json.dumps({"where": {"id": {"inq": libids}}})
res = requests.get(META_API + "/libraries", params={"filter":filters})
if not res.ok:
    raise Exception(res.text)
libs = {i["id"]: i for i in res.json()}


tmp_signatures = signatures[0:2]
signatures = signatures[2:]
tmp_libraries = []
tmplibids = set([s["library"] for s in tmp_signatures])
libids = set([s["library"] for s in signatures])
for i in list(tmplibids):
    tmp_libraries.append(libs[i])
libraries = []
for i in list(libids):
    libraries.append(libs[i])

def populate_temp(libraries, signatures):
    from app.tempmodels import db, TempLibrary, TempSignature
    for i in libraries:
        try:
            entry = TempLibrary(i)
            db.session.add(entry)
        except Exception as e:
            print ("Error inserting tmp library")
            print(e)
            break
            #Rollback if there are errors
            db.session.rollback()
    db.session.commit()
    for i in signatures:
        try:
            entry = TempSignature(i)
            db.session.add(entry)
        except Exception as e:
            print ("Error inserting tmp signature")
            print(e)
            break
            #Rollback if there are errors
            db.session.rollback()
    db.session.commit()

def populate(libraries, signatures):
    from app.models import db, Library, Signature
    for i in libraries:
        try:
            entry = Library(i)
            db.session.add(entry)
        except Exception as e:
            print ("Error inserting tmp library")
            print(e)
            break
            #Rollback if there are errors
            db.session.rollback()
    db.session.commit()
    for i in signatures:
        try:
            entry = Signature(i)
            db.session.add(entry)
        except Exception as e:
            print ("Error inserting tmp signature")
            print(e)
            break
            #Rollback if there are errors
            db.session.rollback()
    db.session.commit()
populate_temp(tmp_libraries,tmp_signatures)
populate(libraries,signatures)
