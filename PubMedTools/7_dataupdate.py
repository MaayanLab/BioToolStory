# Weekly update of citations and Altmetric data

import pandas as pd
import os
import json
import datetime
import sys
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
  time.sleep(0.5)
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
  time.sleep(1)
  res = requests.patch('https://maayanlab.cloud/biotoolstory/metadata-api/' +"signatures/" + tool['id'], json=tool, auth=credentials)
  if (not res.ok):
    print(res.text)
    time.sleep(2)
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
    status = 408
  tool['meta']['url_status'] = {'code': status, 'label': http.client.responses[status]}
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


# push data (tools or journals) directly to the biotoolstory server
def post_data(data,model):
  time.sleep(0.5)
  res = requests.post(API_url%(model,""), auth=credentials, json=data)
  try:
    if not res.ok:
      raise Exception(res.text)
  except Exception as e:
    print(e)
    if model == "signatures":
      f = open(os.path.join(PTH,"data/fail_to_load.txt"), "a")
      f.write(','.join(map(str, data['meta']['PMID'])) + "\n")
      f.close()


def combine_duplicates_tools():
  print("delete duplicates")
  # help function
  def unlist(l):
    for i in l: 
      if type(i) == list: 
        unlist(i) 
      else: 
        pmids.append(i) 
  # end help funuctions
  res = requests.get(API_url%("signatures",""))
  tools_DB = res.json()
  duplicate_urls = find_duplicates(tools_DB)
  il = 0
  kl = len(duplicate_urls)
  for url in duplicate_urls:
    print(il,"out of",kl)
    il = il + 1
    duplicates = [ x for x in tools_DB if x['meta']['tool_homepage_url']== url ]
    dup_tool_names = [x['meta']['Tool_Name'] for x in duplicates]
    # unique names of duplicate tools
    dup_tool_names = [item for item, count in collections.Counter(dup_tool_names).items() if count > 1]
    duplicates = [ x for x in duplicates if x['meta']['Tool_Name'] in dup_tool_names ]
    if len(duplicates) > 1:
      print(duplicates[0]['meta']['PMID'])
      row = find_max(duplicates)
      mn_date = row[1]
      row = row[0]
      citations = 0
      pmids = []
      for k in range(0,len(duplicates)):
        if type(duplicates[k]['meta']['PMID']) != list: 
          pmids.append(duplicates[k]['meta']['PMID'])
        else:
          unlist(duplicates[k]['meta']['PMID'])
        if 'Citationsduin' not in duplicates[k]['meta']:
          duplicates[k]['meta']['Citations'] = 0
        if duplicates[k]['meta']==None:
          duplicates[k]['meta']['Citations'] = 0
        citations = citations + duplicates[k]['meta']['Citations']
        delete_data(duplicates[k],"signatures") # delete from database
      row['meta']['PMID'] = list(set(pmids))
      row['meta']['Citations'] = citations
      row['meta']['first_date'] = mn_date
      post_data(row,"signatures")


if __name__ == '__main__':
  res = requests.get(API_url%('signatures',""))
  tools_DB = res.json()
  counter = 0
  for tool in progressbar.progressbar(tools_DB[0:]):
    # update citations
    citations = 0
    counter = counter +1
    if counter % 4000 == 0:
      time.sleep(60*60*1) # sleep for 1hr
    for pmid in tool['meta']['PMID']:
      citations = citations + len(who_cited(pmid))
    tool['meta']['Citations'] = citations
    # update Altmetric data
    tool = Altmetric(tool)
    tool['meta']['$validator'] = '/dcic/signature-commons-schema/v5/core/unknown.json'
    tool = testURL(tool)
    f = update(tool)
    if f == "error":
      print(str(datetime.now()))
      break
  #combine_duplicates_tools()
  refresh()
  dropbox(tools_DB)





