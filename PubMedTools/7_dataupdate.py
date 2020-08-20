# Weekly update of citations and Altmetric data

import pandas as pd
import os
import json
import datetime
import sys
import time
from datetime import datetime
import re
from dotenv import load_dotenv
import numpy as np
import ast
import requests
from Bio import Entrez
import time
import progressbar
from requests.auth import HTTPBasicAuth
import dropbox
from pandas import ExcelWriter

load_dotenv(verbose=True)
PTH = os.environ.get('PTH_A') # PTH = "/home/maayanlab/Tools/"
API_url = os.environ.get('API_URL')
username = os.getenv("USERNAME")
password = os.getenv("PASSWORD")
credentials = HTTPBasicAuth(username, password)
Entrez.email = os.environ.get('EMAIL')
API_KEY = os.environ.get('API_KEY')
DROPBOX_ACCESS_TOKEN = os.environ.get('DROPBOX_ACCESS_TOKEN')


# Articles that cite a given article ONLY covers journals indexed for PubMed Central
def who_cited(pmid):
  # get pmc_ids
  results = Entrez.read(Entrez.elink(dbfrom="pubmed", db="pmc",
                                  api_key = API_KEY,
                                  usehistory ='y',
                                  retmax = 10000000,
                                  LinkName="pubmed_pmc_refs", id=pmid))
  if len(results[0]['LinkSetDb'])>0:
    pmc_ids = [link["Id"] for link in results[0]["LinkSetDb"][0]["Link"]]
  else:
    pmc_ids=[]
  return(pmc_ids)


# update tool data
def update(tool):
  res = requests.patch('https://maayanlab.cloud/biotoolstory/metadata-api/' +"signatures/" + tool['id'], json=tool, auth=credentials)
  if not res.ok:
    print(res.text)
    return ("error")
  

def iskey(data, key):
  if key in str(data):
    return(data[key])
  else:
    return('')


def Altmetric(tool):
  for pmid in tool['meta']['PMID']:
    url = 'https://api.altmetric.com/v1/pmid/'+str(pmid)
    try:
      r = requests.get(url)
      altmetric_data = r.json()
      tool['meta']['Altmetric_Score'] = iskey(altmetric_data,'score')
      tool['meta']['Readers_Count'] = iskey(altmetric_data,'readers_count')
      tool['meta']['Readers_in_Mendeley'] = iskey(altmetric_data['readers'],'mendeley')
      tool['meta']['Readers_in_Connotea'] = iskey(altmetric_data['readers'],'connotea')
      tool['meta']['Readers_in_Citeulike'] = iskey(altmetric_data['readers'],'citeulike')
      tool['meta']['Cited_By_Posts_Count'] = iskey(altmetric_data,'cited_by_posts_count')
      tool['meta']['Twitter_accounts_that_tweeted_this_publication'] = iskey(altmetric_data,'cited_by_tweeters_count')
      tool['meta']['Users_who_mentioned_the_publication_on_Twitter'] = iskey(altmetric_data['cohorts'],'pub')
      tool['meta']['Scientists_who_mentioned_the_publication_on_Twitter'] = iskey(altmetric_data['cohorts'],'sci')
      tool['meta']['Mentions_in_social_media'] = iskey(altmetric_data,'cited_by_feeds_count')
      tool['meta']['Facebook_Shares'] = iskey(altmetric_data,'cited_by_fbwalls_count')
      time.sleep(2)
    except Exception as e:
      print(e)
  return(tool)


# test if url is available
def testURL(tool):
  url = tool['meta']['tool_homepage_url']
  try:
    request = requests.head(url,allow_redirects=False, timeout=10)
    status = request.status_code
  except:
    status = "error"
  tool['meta']['url_status'] = str(status)
  return(tool)
  
# update the website after petching data
def refresh():
  res = requests.get("https://maayanlab.cloud/biotoolstory/metadata-api/optimize/refresh", auth=credentials)
  print(res.ok)
  res = requests.get("https://maayanlab.cloud/biotoolstory/metadata-api/"+"optimize/status", auth=credentials)
  while not res.text == "Ready":
    time.sleep(1)
    res = requests.get("https://maayanlab.cloud/biotoolstory/metadata-api"+"/optimize/status", auth=credentials)
  res = requests.get("https://maayanlab.cloud/biotoolstory/metadata-api/"+"summary/refresh", auth=credentials)
  print(res.ok)
  

# backup data in dropbox
class TransferData:
  def __init__(self, access_token):
    self.access_token = access_token
  def upload_file(self, file_from, file_to):
    dbx = dropbox.Dropbox(self.access_token)
    #dbx = dropbox.DropboxTeam(access_token)
    with open(file_from, 'rb') as f:
      dbx.files_upload(f.read(), file_to, mode=dropbox.files.WriteMode.overwrite)


def dropbox(tools_DB):
  df = pd.json_normalize(tools_DB)
  df.to_excel(os.path.join(PTH,'data/dump.xlsx'),index=False)
  transferData_a = TransferData(DROPBOX_ACCESS_TOKEN)
  file_from = os.path.join(PTH,'data/dump.xlsx')
  file_to = '/BioToolStory/dump.xlsx'  # The full path to upload the file to, including the file name
  transferData_a.upload_file(file_from, file_to)
  os.remove(file_from)


if __name__ == '__main__':
  res = requests.get(API_url%('signatures',""))
  tools_DB = res.json()
  for tool in progressbar.progressbar(tools_DB[0:]):
    # update citations
    citations = 0
    for pmid in tool['meta']['PMID']:
      citations = citations + len(who_cited(pmid))
    tool['meta']['Citations'] = citations
    # update Altmetric data
    tool = Altmetric(tool)
    tool['meta']['$validator'] = '/dcic/signature-commons-schema/v5/core/unknown.json'
    tool = testURL(tool)
    f = update(tool)
    if f == "error":
      break
  refresh()
  dropbox(tools_DB)


#==================================================== update query to existing journals ===================================================================
#res = requests.get(API_url%('libraries',""))
#journal_DB = res.json()
# for jour in journal_DB:
#       ... do some updates to the data here...
#       push the updated journal back
#       res = requests.patch('https://maayanlab.cloud/toolstory/meta-api/' +"libraries/" + jour['id'], json=jour, auth=credentials)
#       if not res.ok:
#         print(jour)
#         print(res.text)
#         break
