# This script creates the following: 
# 1. collect articles from Pubmed as jsons in /data/jsons
# 2. open the files and save articles that have a link in their title or abstract in /data/tools

from Bio import Entrez
import os
from os import path
import pandas as pd
import datetime
import gzip
import json
import time
import re
import sys
from dotenv import load_dotenv

load_dotenv(verbose=True)

start = str(sys.argv[1])
end = str(sys.argv[2])
loop_index = int(str(sys.argv[3]))
print(start, end)
s = start.replace("/","")
en = end.replace("/","")
PTH = os.environ.get('PTH_A')
Entrez.email = os.environ.get('EMAIL')
API_KEY = os.environ.get('API_KEY')

# returns a list of PubMedCentral ids between dates
def article_links(start_date = None, end_date = None):
  print("collecting PubMed from",start_date,"to",end_date)
  handle = Entrez.esearch(db="pubmed", term='("%s"[Date - Publication] : "%s"[Date - Publication])' %(start_date, end_date),
                              api_key=API_KEY,
                              usehistory ='y',
                              retmax = 1000000
                              )
  records = Entrez.read(handle)
  return (records['IdList'])


# collect data from pubmed_id
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
    if iteration%9==0:
      print("sleep")
      #time.sleep(1)
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
    except Exception as ex:
      print(ex,'at line 89')

  
if __name__ == '__main__':
  if not os.path.isdir(os.path.join(os.path.join(PTH,'data/jsons_'+s+'_'+en))):
    os.mkdir(os.path.join(PTH,'data/jsons_'+s+'_'+en))
  if not os.path.isdir(os.path.join(os.path.join(PTH,'data/tools_'+s+'_'+en))):
    os.mkdir(os.path.join(PTH,'data/tools_'+s+'_'+en))
  if not os.path.isdir(os.path.join(os.path.join(PTH,'data/vectors'))):
    os.mkdir(os.path.join(PTH,'data/vectors'))
  # get pubmeds_ids between dates
  PubMedIds = article_links(start,end) # start/ end dates in format 'YYYY/MM/DD'
  # collect data by pubmed_id
  missing_pubmed_ids = collectData(PubMedIds,loop_index,s,en) # the second input is the last file name in ./data/jsons_.../ (where the loop failed)
  # read json files and parse (each json file contains up to 200 articles)
  filesnames = [ x for x in os.listdir(os.path.join(PTH,'data/jsons_'+s+'_'+en)) if x.endswith("json.gz") ]
  k = len(filesnames)
  i=0
  for file in filesnames:
    print(i ,"out of", k)
    i = i + 1
    articles = os.path.join(PTH,'data/jsons_'+s+'_'+en,file)
    parsejsons(articles,s,en)
