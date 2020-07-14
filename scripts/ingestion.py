import os
import json
import requests
from requests.auth import HTTPBasicAuth
from dotenv import load_dotenv
import time
load_dotenv(dotenv_path="../.env")

APIURL = os.getenv("APIURL")
USERNAME = os.getenv("USERNAME")
PASSWORD = os.getenv("PASSWORD")

auth = HTTPBasicAuth(USERNAME,PASSWORD)

with open("../data/libraries.json") as o:
    libraries = json.loads(o.read())

with open("../data/signatures_names.json") as o:
    signatures = json.loads(o.read())


def empty_cleaner(obj):
    if type(obj) == str:
        obj = obj.strip()
        if obj == "":
            return None
        else:
            return obj
    elif type(obj) == list:
        new_list = []
        for i in obj:
            v = empty_cleaner(i)
            if v:
                new_list.append(v)
        if len(new_list) > 0:
            return new_list
        else:
            return None
    elif type(obj) == dict:
        new_dict = {}
        for k,v in obj.items():
            val = empty_cleaner(v)
            if val:
                new_dict[k.replace("'","").replace(" ","_")] = val
        if len(new_dict) > 0:
            return new_dict
        else:
            return None
    else:
        return obj

print("deleting signatures...")
while True:
    try:
        res = requests.get(APIURL+"/signatures")
        for s in res.json():
            r = requests.delete(APIURL+"/signatures/"+s["id"], auth=auth)
            time.sleep(0.1)
            if not r.ok:
                print(s["id"])
                raise Exception(r.text)
        else:
            break
    except Exception as identifier:
        time.sleep(5)        
        continue


print("deleting libraries...")
while True:
    try:
        res = requests.get(APIURL+"/libraries")
        for l in res.json():
            r = requests.delete(APIURL+"/libraries/"+l["id"], auth=auth)
            if not r.ok:
                print(l["id"])
                raise Exception(r.text)
        else:
            break
    except Exception as identifier:
        time.sleep(5)        
        continue



print("adding libraries...")
while True:
    try:
        res = requests.get(APIURL+"/libraries")
        libs = [i["id"] for i in res.json()]
        for l in libraries:
            if l["id"] not in libs:
                r = requests.post(APIURL+"/libraries/", json=empty_cleaner(l), auth=auth)
                time.sleep(0.3)
                if not res.ok:
                    raise Exception(r.text)
        else:
            break
    except Exception as identifier:
        time.sleep(5)        
        continue


print("adding signatures...")
while True:
    try:
        res = requests.get(APIURL+"/signatures")
        sigs = [i["id"] for i in res.json()]
        print(len(sigs))
        for s in signatures:
            if s["id"] not in sigs:
                if s["meta"]["KeywordList"] == "[]":
                    s["meta"]["KeywordList"] = []
                r = requests.post(APIURL+"/signatures/", json=empty_cleaner(s), auth=auth)
                time.sleep(0.3)
                if not r.ok:
                    raise Exception(r.text)
        else:
            break
    except Exception as identifier:
        print(identifier)
        time.sleep(5)        
        continue

# failed_libraries = []
# res = requests.get(APIURL+"/libraries")
# libs = [i["id"] for i in res.json()]
# for l in libraries:
#     if l["id"] not in libs:
#         res = requests.post(APIURL+"/libraries/", json=empty_cleaner(l), auth=auth)
#         time.sleep(0.3)
#         if not res.ok:
#             failed_libraries.append(l["id"])

# with open("failed_libraries.json", "w") as o:
#     o.write(json.dumps(failed_libraries))

# res = requests.get(APIURL+"/signatures")
# sigs = [i["id"] for i in res.json()]

# failed_signatures = []
# for l in signatures:
#     if l["id"] not in sigs:
#         res = requests.post(APIURL+"/signatures/", json=empty_cleaner(l), auth=auth)
#         time.sleep(0.3)
#         if not res.ok:
#             failed_signatures.append(l["id"])

# with open("failed_signatures.json", "w") as o:
#     o.write(json.dumps(failed_signatures))


print("refreshing...")
res = requests.get(APIURL+"/optimize/refresh", auth=auth)
print(res.ok)
res = requests.get(APIURL+"/summary/refresh", auth=auth)
print(res.ok)