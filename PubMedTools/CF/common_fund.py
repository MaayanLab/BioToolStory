# Collect common fund
from dotenv import load_dotenv
load_dotenv(verbose=True)
import requests
import pandas as pd
import os
import time
from bs4 import BeautifulSoup
import time
from Bio import Entrez
from os import path
import datetime
import gzip
import json
import re
import sys
from urllib.parse import quote

# PubMed account 
Entrez.email = os.environ.get('EMAIL')
API_KEY = os.environ.get('API_KEY') 

# set path to directory
PTH = os.environ.get('PTH')

# set dates to collect articles from Pubmed
start = str(sys.argv[1])
end = str(sys.argv[2])
s = start.replace("/","")
en = end.replace("/","")

# create dir
if not os.path.isdir(os.path.join(os.path.join(PTH,'data'))):
  os.mkdir(os.path.join(PTH,'data'))
  
if not os.path.isdir(os.path.join(os.path.join(PTH,'data/jsons_'+s+'_'+en))):
  os.mkdir(os.path.join(PTH,'data/jsons_'+s+'_'+en))
  
if not os.path.isdir(os.path.join(os.path.join(PTH,'data/tools_'+s+'_'+en))):
  os.mkdir(os.path.join(PTH,'data/tools_'+s+'_'+en))
  
if not os.path.isdir(os.path.join(os.path.join(PTH,'data/vectors'))):
  os.mkdir(os.path.join(PTH,'data/vectors'))

# help functions
# collect data from pubmed
def collectData(PubMedIds, start_index, s, en):
  MaxRounds=max(1,round(len(PubMedIds)/100,0))
  iteration=round(len(PubMedIds)/100,0)  - (round((len(PubMedIds) - start_index)/100,0))
  missing=list()
  for i in range(start_index,len(PubMedIds),100):
    print("collecting from pubmed. Round",iteration, 'out of', MaxRounds)
    ids=PubMedIds[i:99+i]
    ids=str(ids).strip('[]') # create comma-separated string
    try:
      handleS = Entrez.efetch(db="pubmed", id=ids,rettype="xml", api_key=API_KEY,usehistory ='y',retmax = 10000000)
      records = Entrez.read(handleS)
      f = gzip.open(os.path.join(PTH,'data/jsons_'+ s +'_'+ en , str(i) + '.json.gz'), 'wb')
      f.write((json.dumps(records)).encode('utf-8')) # save record to gz file as json
      f.close()
    except Exception as e:
      print(e, "round",i)
      missing.append(i)
    iteration = iteration + 1
    if iteration%10==0:
      print("sleep")
      time.sleep(5)
  handleS.close()
  return(missing)
  
  
def is_key(keys, value):
  for key in keys:
    if key in value:
      value = value.get(key)
    else:
      value = ""
      break
  return(value)
  
  
# break jsons to single articles by pubmedid
def parsejsons(articles,s,en):
  with gzip.open(articles) as fin:
    try:
      for line in fin:
        json_obj = json.loads(line)
        for record in json_obj['PubmedArticle']:
          article = is_key(['MedlineCitation'],record)
          PMID = is_key(['PMID'],article)
          with gzip.open(os.path.join(PTH,'data/tools_'+s+'_'+en,PMID+".json.gz"), 'wt', encoding="ascii") as f:
            #print(os.path.join(PTH,'data/tools_'+s+'_'+en,PMID+".json.gz"))
            json.dump(record, f)
    except:
      import traceback as tb
      tb.print_exc()


# STEP 1 -- get links from common fund and collect project title ----------- ----------- ----------- ----------- ----------- ----------- -----------
def read_html(URL):
  html_text = requests.get(URL).text
  return BeautifulSoup(html_text, 'html.parser')

soup = read_html('https://commonfund.nih.gov/grants/fundedresearch#tab3')
data = soup.findAll("div", {"class": "fundingopp_tab_content tab3"})
links = data[0].findAll('a')


for a in links:
  CF_program = a.text
  print(links.index(a),CF_program)
  if "https://commonfund.nih.gov/" in a['href']:
    html_page=read_html(a['href']) # call 1
  else:
    html_page=read_html('https://commonfund.nih.gov/'+a['href']) # call 1
  print('sleep...5')
  time.sleep(5)
  tables = html_page.findAll('table')# ,'responsive-data-table')
  for table in tables:
    table_links = table.findAll('a')
    if len(table_links) == 0:
      continue
    df = pd.read_html(str(table))[0]
    df = df[~df.iloc[:,0].str.contains("PI Name",na=False)]
    df = df[~df.eq(df.iloc[:, 0], axis=0).all(1)] # remove rows having the same value in all columns
    df = df.dropna(axis=1, how='all') # remove columns that have all NaNs
    df = df[~df.eq(df.iloc[:, 0], axis=0).all(1)] # remove rows having the same value in all columns
    df.reset_index(drop=True, inplace=True)
    df['projectnumber'] = ''
    df['CF_program'] = ''
    i=0
    for link in table_links:
      print(link)
      if link.has_attr('href'):
        if 'project' in link['href']:
          indx = link['href'].find('projectnumber')
          if indx > 0:
            df['projectnumber'][i] = link['href'][indx+14:]
            df['CF_program'][i] = CF_program
          else:
            if "https://" in link['href'] or "http://" in link['href']:
              html_page = read_html(link['href']) # call 1
            else:
              html_page = read_html("https://" + link['href']) # call 2
            df['projectnumber'][i] = html_page.findAll('td')[1].text.strip().split()[0]
            df['CF_program'][i] = CF_program
            print('sleep...10')
            time.sleep(10)
          i = i + 1
    df.to_csv(os.path.join(PTH,'data/NIH_crawler3.csv'), mode='a', header=False)

# --- search missing NA project numbers
# STEP 2 -- use Reporter API to get missing project number  ----------- ----------- ----------- ----------- ----------- ----------- ----------- ----------- --
df = pd.read_csv(os.path.join(PTH,"data/NIH_crawler3.csv"))
df.columns = ['index','PI Name','Institution Name','Title','Project number','Program']
i=0
for title in df['Title'].tolist():
  print(i)
  y = df.iloc[i]['Project number']
  if (type(y) == float) or ('Contact' in y ) or (y == None) : # detect missing project numbers
    print(i, title)
    try:
      URL='https://api.federalreporter.nih.gov/v1/Projects/search?query=text%3A' + quote(title) + '%24textFields%3Atitle&offset=1&limit=50&sortBy=fy&sortOrder=asc'
      r = requests.get(URL)
      x=r.json()
      RES_DF = pd.DataFrame(x['items'])
      if len(RES_DF) > 0:
        df.iloc[i]['Project number'] = RES_DF['projectNumber'].tolist()
      else:
        df.iloc[i]['Project number'] = 'Empty'
    except Exception as e:
      print(e, i)
  i=i+1
df.to_csv(os.path.join(PTH,"data/NIH_CF.csv"),index=False)


# STEP 3 -- get pubmed ids by project number  ----------- ----------- ----------- ----------- ----------- ----------- ----------- ----------- ----------- -----------
df = pd.read_csv(os.path.join(PTH,'data/NIH_CF.csv'))
df = df.dropna()
df['pnum'] = ''
for i in range(0,len(df)):
  print(i)
  w = df.iloc[i]['Project number']
  if type(w) != float:
    inx = w.find("-")
    if inx != -1:
      w = w[4:inx]
    df.iloc[i, df.columns.get_loc('pnum')] = w


# returns a list of PubMedCentral ids between dates
def article_links(q):
  handle = Entrez.esearch(db="pubmed", term=q,
                              api_key=API_KEY,
                              usehistory ='y',
                              retmax = 10000000
                              )
  records = Entrez.read(handle)
  return (records['IdList'])

# get pmids
df['pmids'] = ''
for i in range(0,len(df)):
  print(i,'out of',len(df))
  try:
    x = article_links(df.iloc[i, df.columns.get_loc('pnum')])
    df.iloc[i, df.columns.get_loc('pmids')] = ','.join(x)
  except Exception as e:
    print(e)
df = df.drop_duplicates()
df.to_csv(os.path.join(PTH,"data/NIH_pmids.csv"))

# STEP 3 Btools: collect tools by pmids--> go to 1_collect_data.py and run collectData(PubMedIds,0,e,s) ----------- ----------- ----------- ----------- -----------
df_pmid = pd.read_csv(os.path.join(PTH,"data/NIH_pmids.csv"))

test_list = []
df_pmid = df_pmid[~df_pmid['pmids'].isna()]

for i in range(0,len(df_pmid)):
  print(i)
  pmids = df_pmid.iloc[i,df_pmid.columns.get_loc('pmids')]
  pmids = pmids.split(',')
  test_list = test_list + pmids
  
test_list = set(test_list)
test_list = list(test_list)

# STEP 4 -- get data from pubmed for each pubmed id ----------- ----------- ----------- ----------- ----------- ----------- ----------- ----------- ----------- -----------
# run function collectData loacated at .../PubMedTools/1_collect_data.py
collectData(test_list,0,s,en)
filesnames = [ x for x in os.listdir(os.path.join(PTH,'data/jsons_'+s+'_'+en)) if x.endswith("json.gz") ]
for file in filesnames:
  print(file)
  articles = os.path.join(PTH,'data/jsons_'+s+'_'+en,file)
  parsejsons(articles,s,en)
