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

while True:
    res = requests.get(APIURL+"/signatures")
    if res.ok:
        tools = res.json()
        break
    else:
        time.sleep(1)
with open("../data/patched.txt") as o:
    patched = set(o.read().split("\n"))
    print(len(patched))
    
with open("../data/patched.txt", "a+") as o:
    for t in tools:
        if t["id"] not in patched:
            if len(patched) % 1000 == 0:
                print(len(patched))
            fullname = t["meta"].pop("FullNames", "")
            year = t["meta"].pop("year", None)
            if year:
                t["meta"]["Year"] = str(year)
            if "Author_Information" in t["meta"]:
                authors = []
                for a in t["meta"]["Author_Information"]:
                    ForeName = a.get("ForeName", "")
                    LastName = a.get("LastName", "")
                    Suffix = a.get("Suffix", "")
                    CollectiveName = a.get("CollectiveName", "")
                    FullName = ("%s %s %s" % (ForeName, LastName, Suffix)).strip() or CollectiveName
                    if FullName:
                        a["Name"] = FullName
                    authors.append(a)
                t["meta"]["Author_Information"] = authors
                t["meta"]["Last_Author"] = authors[-1]
            c = 0
            success = False
            while c<5:
                try:
                    r = requests.patch(APIURL+"/signatures/"+t["id"], json=t, auth=auth)
                    success = True
                    break
                except Exception as e:
                    print("Failed at %s, retrying..."%t["id"])
                    time.sleep(1)
                    c+=1
            if not r.ok and not success:
                print(res.text)
                break
            else:
                patched.add(t["id"])
                o.write(t["id"]+"\n")

# with open("../data/patched.txt", "w") as o:
#     for i in patched:
#         o.write(i+"\n")