# Tables: resources <program,uuid> --> libraries <journal,ISSN> --> signatures <tools,pmid>
# test: http://[::1]:3000/signature-commons-metadata-api/libraries/
import requests
import urllib.request
import json
import sys
import os
import time
import re
import pandas as pd
from requests.auth import HTTPBasicAuth
from dotenv import load_dotenv
import uuid
from crossref.restful import Works
from crossref.restful import Journals
import numpy as np
import requests as req
import itertools
from bs4 import BeautifulSoup
import lxml
import ast
from datetime import datetime
import collections

load_dotenv(verbose=True)
PTH = os.environ.get('PTH_A','/users/alon/desktop/github/maayanlab/btools/')
tools_list = []
journal_list = []

# load journals from json file
with open("/users/alon/desktop/journals.json") as o:
  journal_list = json.loads(o.read())

with open("/users/alon/desktop/tools.json") as o:
  tools_list = json.loads(o.read())
  

def write_to_file(schema):
    if schema == "tools":
        with open(os.path.join(PTH,schema + '.json'), 'w') as outfile:
            json.dump(tools_list, outfile)
    else:
        with open(os.path.join(PTH,schema + '.json'), 'w') as outfile:
            json.dump(journal_list, outfile)


def post_data(data,model):
  if model == "tools":
    tools_list.append(data)
  else:
    journal_list.append(data)


def remove_data(data,model):
  if model == "tools":
    tools_list.remove(data)
  else:
    journal_list.remove(data)


# fix pubmed json 
def fix_dirty_json(text,flg=False):
  if isinstance(text, pd.Series):
    text = text.tolist()[0]
  try:
    x = ast.literal_eval(text)
  except:
    if(flg):
      x = text
    else:
      x = ''
  return(x)
  

def find_max(duplicates):
  mx = duplicates[0]
  mn_date = 'None'
  if 'Article_Date' in mx['meta']:
    y = mx['meta']['Article_Date'][0]['Year']
    m = mx['meta']['Article_Date'][0]['Month']
    d = mx['meta']['Article_Date'][0]['Day']
    mx_date = datetime.strptime(y+"-"+m+"-"+d, '%Y-%m-%d')
    mn_date = datetime.strptime(y+"-"+m+"-"+d, '%Y-%m-%d')
    for tool in duplicates:
      try:
        y = tool['meta']['Article_Date'][0]['Year']
        m = tool['meta']['Article_Date'][0]['Month']
        d = tool['meta']['Article_Date'][0]['Day']
        dt = datetime.strptime(y+"-"+m+"-"+d, '%Y-%m-%d')
        if mx_date > dt:
          mx = tool
          mx_date = dt
        if mn_date < dt:
          mn_date = dt
      except:
        pass
  return([mx,mn_date])
  

def find_duplicates(tools_DB):
    urls = []
    for i in range(len(tools_DB)):
        urls.append(tools_DB[i]['meta']['tool_homepage_url'])
    # a list of unique duplicated urls
    dup_links = [item for item, count in collections.Counter(urls).items() if count > 1]
    return(dup_links)

  
def combine_duplicates_tools():
  def unlist(l):
    for i in l: 
      if type(i) == list: 
        unlist(i) 
      else: 
        pmids.append(i) 
  #tools_DB = tools_list
  duplicate_urls = find_duplicates(tools_list)
  il = 0
  kl = len(duplicate_urls)
  for url in duplicate_urls:
    print(il,"out of",kl)
    il = il + 1
    duplicates = [ x for x in tools_list if x['meta']['tool_homepage_url']== url ]
    dup_tool_names = [x['meta']['Tool_Name'] for x in duplicates]
    # unique names of duplicate tools
    dup_tool_names = [item for item, count in collections.Counter(dup_tool_names).items() if count > 1]
    duplicates = [ x for x in duplicates if x['meta']['Tool_Name'] in dup_tool_names ]
    if len(duplicates) > 1:
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
            tools_list.remove(duplicates[k]) # delete from database
        row['meta']['PMID'] = list(set(pmids))
        row['meta']['Citations'] = citations
        row['meta']['first_date'] = mn_date
        tools_list.append(row)
    

  
def reorder_colmns(df):
  columns = [ 
              "Tool_URL",
              "Tool_Name",                                                               
              "Tool_Description",
              "PMID",
              "DOI",
              "Article_Title",                                                              
              "Abstract",
              "Author_Information",                                                          
              "Electronic_Location_Identifier",
              "Publication_Type",                                                            
              "Grant_List",                                                                 
              "Chemical_List",
              "Citations",
              "Article_Language",                                                         
              "KeywordList",
              "Last_Updated",                                                             
              "Added_On",
              "Published_On",                                                                
              "Article_Date",
              "Journal",                                                                     
              "ISSN",
              "Journal_Title",                                                               
              "Altmetric_Score",
              "Readers_Count",
              "Readers_in_Mendeley",                                                         
              "Readers_in_Connotea",
              "Readers_in_Citeulike",                                                        
              "Cited_By_Posts_Count",
              "Twitter_accounts_that_tweeted_this_publication",                         
              "Users_who_mentioned_the_publication_on_Twitter",
              "Scientists_who_mentioned_the_publication_on_Twitter",                        
              "News_sources_that_mentioned_the_publication",
              "Mentions_in_social_media",                                                    
              "Facebook_Shares",
    ]
  return(df[columns])


def push_new_journal(ISSN):
  try:
    time.sleep(1)
    url = 'http://api.crossref.org/journals/' + urllib.parse.quote(ISSN)
    resp = req.get(url)
    text = resp.text
    resp = json.loads(text)
    jour = resp['message']['title']
    Publisher = resp['message']['publisher']
  except Exception as e:
    print("error in push_new_journal() --> ", e)
    url = ''
    jour = 'NA'
    Publisher = 'NA'
  new_journal = {'$validator': '/dcic/signature-commons-schema/v5/core/library.json', 
  'id': str(uuid.uuid4()),
  'dataset': 'journal',
  'dataset_type': 'rank_matrix', 
  'meta': {
    'name': jour,
    'NLM TA': 'NA',
    'pISSN': 'NA', 
    'eISSN': ISSN, 
    'Publisher': Publisher,
    'LOCATORplus ID': 'NA', 
    'Latest issue': 'NA', 
    'Earliest volume': 'NA', 
    'Free access': 'NA', 
    'Open access': 'NA', 
    'Participation level': 'NA', 
    'Deposit status': 'NA',
    'homepage': 'http://www.ncbi.nlm.nih.gov/pmc/journals/1811/', 
    '$validator': 'https://raw.githubusercontent.com/MaayanLab/btools-ui/redux/validators/btools-journal.json', 
    'icon': 'NA'}
    }
  post_data(new_journal,"journal")
  return(new_journal['id'])


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
        new_dict[k] = val
    if len(new_dict) > 0:
      return new_dict
    else:
      return None
  else:
    return obj


def to_human_time(text):
  try:
    t = datetime.utcfromtimestamp(text).strftime('%Y-%m-%d')
  except:
    t = ''
  return t


def remove_tools(df):
  # remove tools with the same names but different url
  x = df[df.duplicated(['Tool_Name'])]
  y = x[x.duplicated(['Tool_URL'])]['PMID'].tolist()
  x = x[~x['PMID'].isin(y)]['PMID'].tolist()
  df = df[~df['PMID'].isin(x)]
  # remove tools with long/short names
  df = df[(df['Tool_Name'].str.len() > 2) & (df['Tool_Name'].str.len() < 31)]
  df = df.reset_index(drop=True)
  # remove tools with the same PMID (keep first one)
  df = df.drop_duplicates(subset='PMID', keep="first")
  return(df)


def push_tools(df):
  df = df.replace(np.nan, '', regex=True)
  df = remove_tools(df)
  df=rename(df)
  df = reorder_colmns(df)
  df.rename(columns={'Tool_URL':'tool_homepage_url'}, inplace=True)
  k = len(df)
  i = 0
  keep = df.columns.drop(['Author_Information','Article_Date'])
  for tool in df.to_dict(orient='records'):
    print('Uploaded',i,'tools out of',k)
    i = i + 1
    data = {}
    data["$validator"] = '/dcic/signature-commons-schema/v5/core/signature.json'
    data["id"] = str(uuid.uuid4()) # create random id
    ISSN = tool['ISSN']
    key = [x['id'] for x in journal_list if x['meta']['eISSN']==ISSN ]
    if len(key)>0:
      data["library"] = key[0] # uuid from libraries TABLE
    else:
      data["library"]  = push_new_journal(ISSN)
    data["meta"] = { key: tool[key] for key in keep }
    data["meta"]["Author_Information"] = fix_dirty_json(tool['Author_Information'])
    data["meta"]["Article_Date"] =  fix_dirty_json(tool['Article_Date'])
    data["meta"]["Abstract"] =  fix_dirty_json(tool['Abstract'],flg=True)
    data["meta"]["Article_Language"] =  fix_dirty_json(tool['Article_Language'])
    data["meta"]["Electronic_Location_Identifier"] =  fix_dirty_json(tool['Electronic_Location_Identifier'])
    data["meta"]["Publication_Type"] =  fix_dirty_json(tool['Publication_Type'])
    data["meta"]["Grant_List"] =  fix_dirty_json(tool['Grant_List'])
    data["meta"]["Chemical_List"] =  fix_dirty_json(tool['Chemical_List'])
    data["meta"]["KeywordList"] =  fix_dirty_json(tool['KeywordList'])
    data["meta"]["Last_Updated"] = to_human_time(data["meta"]["Last_Updated"])
    data["meta"]["Added_On"] = to_human_time(tool['Added_On'])
    data["meta"]["Published_On"] = to_human_time(tool['Published_On'])
    data["meta"]["$validator"] = '/dcic/signature-commons-schema/v5/core/unknown.json'
    data["meta"] = empty_cleaner(data['meta']) # delete empty fields
    post_data(data,"tools")


# load journal data to database
def push_journals():
  # get existing journal names from DB
  journals_DB = journal_list
  j_names = [ journal['meta']['name'] for journal in journals_DB ]
  # download journals data from NCBI
  journals = pd.read_csv('https://www.ncbi.nlm.nih.gov/pmc/journals/?format=csv')
  journals.columns = [
        'name', 'NLM TA', 'pISSN', 'eISSN', 'Publisher',
       'LOCATORplus ID', 'Latest issue', 'Earliest volume', 'Free access',
       'Open access', 'Participation level', 'Deposit status',
       'homepage'
       ]
  journals = journals.fillna('')
  # detect new journals in NCBI that are not in our DB
  journals = journals[~journals['name'].isin(j_names)]
  # push new journals to DB
  counter = 1
  for jor in journals.to_dict(orient='records'):
    data = {}
    data["$validator"] = '/dcic/signature-commons-schema/v5/core/library.json'
    data["id"] = str(uuid.uuid4())
    data["dataset"] = "journal"
    data["dataset_type"] = "rank_matrix"
    data["meta"] = jor
    data["meta"]["$validator"] = "https://raw.githubusercontent.com/MaayanLab/btools-ui/redux/validators/btools-journal.json"
    data["meta"]["icon"] = ""
    post_data(data,"journal")
    print(counter, 'out of', len(journals))
    counter = counter +1

def rename(df):
  df.columns = ['Tool_URL', 'url_status', 'Tool_Name', 'Tool_Description',
         'PMID', 'DOI', 'Article_Title', 'Abstract', 'Author_Information',
         'Electronic_Location_Identifier', 'Publication_Type',
         'Copyright_Information', 'Grant_List', 'Chemical_List',
         'Cited (By PMC_ids)', 'Citations', 'Article_Language', 'KeywordList',
         'Last_Updated', 'Added_On', 'Published_On', 'Article_Date', 'Journal',
         'ISSN', 'Journal_Title', 'Altmetric_Score',
         'Publicaions_in_this_journal', 'Readers_Count', 'Readers_in_Mendeley',
         'Readers_in_Connotea', 'Readers_in_Citeulike', 'Cited_By_Posts_Count',
         'Twitter_accounts_that_tweeted_this_publication',
         'Users_who_mentioned_the_publication_on_Twitter',
         'Mean_score_for_publications',
         'Scientists_who_mentioned_the_publication_on_Twitter',
         'News_sources_that_mentioned_the_publication',
         'Mentions_in_social_media', 'Facebook_Shares']
  return(df)


# main()
onlyfiles = os.listdir(os.path.join(PTH,'data/toos_me/'))
tools_list = []
df = pd.read_csv(os.path.join(PTH,'data/toos_me',onlyfiles[0]))
for file in onlyfiles[1:]:
  df = pd.concat([df, pd.read_csv(os.path.join(PTH,'data/toos_me',file))])
push_tools(df)
