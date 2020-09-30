import pandas as pd
import json
import os,os.path
import tweepy
import random
import string
from tweepy import OAuthHandler, Stream, StreamListener
from dotenv import load_dotenv
import nltk
from nltk.tokenize import RegexpTokenizer
from nltk.corpus import stopwords
import difflib
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import requests
import sys
import re
from Bio import Entrez
import datetime
import gzip
import re
import en_core_web_sm
from itertools import groupby
import csv
import numpy as np
from bs4 import BeautifulSoup
import subprocess
nltk.download('stopwords')
nlp = en_core_web_sm.load()

load_dotenv()

Entrez.email = os.environ.get('EMAIL')
API_KEY = os.environ.get('API_KEY')

# get environment vars from .env
PTH = os.environ.get('PTH_A') # PTH="/home/maayanlab/enrichrbot/DM/"

# enrichr credentials
CONSUMER_KEY=os.environ.get('CONSUMER_KEY')
CONSUMER_SECRET=os.environ.get('CONSUMER_SECRET')
ACCESS_TOKEN=os.environ.get('ACCESS_TOKEN')
ACCESS_TOKEN_SECRET=os.environ.get('ACCESS_TOKEN_SECRET') 

# Twitter authentication
auth = tweepy.OAuthHandler(CONSUMER_KEY, CONSUMER_SECRET)
auth.set_access_token(ACCESS_TOKEN, ACCESS_TOKEN_SECRET)
api = tweepy.API(auth, wait_on_rate_limit=True)

keeplist = "=./" #characters to keep in url
stop_words = set(stopwords.words('english'))
stop_words.update(set(["one","two","three","four","five","six","seven","nine","ten","zero"]))

# read a list of keywords to ignore
f = open(os.path.join(PTH,'RemoveKeyWords.txt'), 'r')
blacklist = f.readlines()
blacklist = [x.rstrip('\n') for x in blacklist]
f.close()


def collect_data(pmid):
  try:
      handleS = Entrez.efetch(db="pubmed", id=pmid,rettype="xml", api_key=API_KEY)
      records = Entrez.read(handleS)
      return(records['PubmedArticle'][0])
  except Exception as e:
      print(e)


def getEntity(title,abstract):
  URL = re.findall("(?P<url>https?://[^\s]+)", abstract) # need to also cathe the sequence 'www'!!!
  # deal with cases where no http is in the url
  ht = abstract[abstract.find("www"):]
  ht = ht[0:ht.find(" ")]
  ht = "http://"+ht
  if ht != "http://":
    URL.append(ht)
  if len(URL) == 0:
    return("")
  cleanurls = []
  for url in URL:
    x = [word for word in blacklist if word in url.lower() ]
    if len(x) == 0:
      cleanurls.append(re.sub(r'[^\w'+keeplist+']', '',url).strip('.'))
  if len(cleanurls) == 0:
    return("")
  print(cleanurls)
  # --- detect tool name -----
  ents=""
  text = str(title)
  if ":" in text:
    ents = text[0:text.index(":")].strip()
    description = text[text.index(":")+1:].strip()
    return([ents],description,cleanurls)
  else:
    doc = nlp(text)
    try:
      fb_ent = Span(doc, 0, 1, label="ORG")
      doc.ents = list(doc.ents) + [fb_ent]
    except:
      doc = nlp(text)
    ents = [e.text for e in doc.ents]
    ents = remove_stop_words(ents)
    length = max([len(list(group)) for key, group in groupby(ents)])
    ents = [max(ents,key=ents.count)] # return the modst frequent element
  if length<= 1:
    doc = nlp(text + " " + abstract)
    ents = [e.text for e in doc.ents]
    ents = remove_stop_words(ents)
    length = max([len(list(group)) for key, group in groupby(ents)])
    if length>1:
      ents = [max(ents,key=ents.count)]
    else:
      ents = list(set(ents))
  # delete punctuation
  title = title.translate(str.maketrans('', '', string.punctuation))
  querywords = title.split()
  resultwords  = [word for word in querywords if word not in ents] # remove entities from title
  if resultwords[-1] in stop_words: # id last word is a stop word
    resultwords  = resultwords[0:-1]
  description = ' '.join(resultwords)
  return(ents,description,cleanurls)
  

def is_key(keys, value):
  for key in keys:
    if key in value:
      value = value.get(key)
    else:
      value = ""
      break
  return(value)


def remove_stop_words(text_list):
  filtered_sentence = [w for w in text_list if not w.lower() in stop_words]
  return(filtered_sentence)


def create_df(df):
  ArticleTitle = df['Article.ArticleTitle'].tolist()[0]
  AbstractText = df['Article.Abstract.AbstractText'].tolist()[0]
  data = getEntity(ArticleTitle,AbstractText)
  df['tool_name'] = [data[0]]
  df['tool_description'] = data[1]
  df['tool_URL'] = [data[2]]
  # clean data
  df['Article.Abstract.AbstractText'] = [ BeautifulSoup(str(x), "lxml").text for x in df['Article.Abstract.AbstractText'] ]
  df['Article.ArticleTitle'] = [ BeautifulSoup(str(x), "lxml").text for x in df['Article.ArticleTitle'] ]
  df['tool_description'] = [ BeautifulSoup(str(x), "lxml").text for x in df['tool_description'] ]
  # delete non alphanomeric characters but keep those in the keeplist
  keeplist = " =./" #characters to keep in url
  df['Article.Abstract.AbstractText'] =[ re.sub(r'[^\w'+keeplist+']', '',x) for x in df['Article.Abstract.AbstractText'] ]
  df['Article.ArticleTitle'] =[ re.sub(r'[^\w'+keeplist+']', '',x) for x in df['Article.ArticleTitle'] ]
  df['tool_description'] =[ re.sub(r'[^\w'+keeplist+']', '',x) for x in df['tool_description'] ]
  return(df)


def pritify(df):
  tmp = []
  for i in range(0,len(df)):
    flg = 0
    x = stringlist2list(df.iloc[i]['tool_URL'])
    print(i)
    if any(isinstance(i, list) for i in x):
      tmp.append( [item for sublist in x for item in sublist] )
      flg = 1
    if len(x) == 1:
      tmp.append( x[0].strip() )
      flg = 1
    if flg == 0:
      tmp.append(x)
  del df['tool_URL']
  df['tool_URL'] = tmp
  return(df)


def stringlist2list(str_list):
  if type(str_list) == float:
    return('')
  while any(isinstance(i, list) for i in str_list):
    str_list = str_list[0]
  if not isinstance(str_list, list):
    str_list = str_list.strip('[]') 
    str_list = str_list.strip("'")
    str_list = str_list.strip('"')
    str_list = str_list.split(",")
    str_list = [x for x in str_list if len(x) >0]
  return(str_list)
  

def keep_first_link(df):
  pattern = re.compile(r"[^a-zA-Z0-9-//?.]+")
  links=[]
  # keep only first link
  for i in range(0,len(df)):
    if isinstance(df.at[i,'tool_URL'], list):
      url = df.at[i,'tool_URL'][0]
    else:
      url = (df.at[i,'tool_URL']).split(",")[0]
    url = url[url.find("http"):]
    index = url.rfind('.')
    url = url[:index+1]+pattern.sub('', url[index:])
    url = url.strip(".")
    url = url.replace("..",".")
    url = url.replace("https//",'https://')
    url = url.replace("http//",'http://')
    links.append(url)
  return(links)


def testURL(df):
  df['status']=''
  for i in range(0,len(df['tool_URL'])):
    url = df.iloc[i]['tool_URL']
    if isinstance(url, list):
      url = url[0].strip("'")
    print(i,url)
    try:
      request = requests.head(url,allow_redirects=False, timeout=5)
      status = request.status_code
    except:
      status = "error"
    df.at[i,'status'] = str(status)
  return(df)
  

def fix_tool_name(df):
  z = len(df)
  for i in range(0,z):
    print(i, 'out of', z)
    tool_name = df['tool_name'].iloc[i]
    # if tool_name is None continue
    if type(tool_name) == float:
      continue
    if isinstance(tool_name, list):
      df.at[i,'tool_name']  = ' '.join(tool_name)
      tool_name = ' '.join(tool_name)
    if len(tool_name.split(',')) > 1:
      if isinstance(df['tool_URL'].iloc[i], list):
        URL = df['tool_URL'].iloc[i][0]
      else:
        URL = df['tool_URL'].iloc[i]
      URL = URL.split('/')
      URL = [j for j in URL if j] # remove empty strings
      if len(URL)>0:
        x = URL[len(URL)-1]
        df['tool_name'].iloc[i] = x[:x.find(".htm")]
  df['tool_name'] = df['tool_name'].str.replace("[", "")
  df['tool_name'] = df['tool_name'].str.replace("]", "")
  df['tool_name'] = df['tool_name'].str.strip("'")
  return(df)
  

def who_cited(pmids):
  # get pmc_ids
  results = Entrez.read(Entrez.elink(dbfrom="pubmed", db="pmc",
                                  api_key = API_KEY,
                                  usehistory ='y',
                                  retmax = 10000000,
                                  LinkName="pubmed_pmc_refs", id=pmids))
  citations = []                              
  for link in results:
    if len(link['LinkSetDb']) > 0:
      citations.append(len(link['LinkSetDb'][0]["Link"]))
    else:
      citations.append(0)
  return(citations)
  

def Altmetric(pmids):
  Frame = pd.DataFrame()
  i=0
  for pmid in pmids:
    try:
      i = i+1
      print('Altmetric', i, 'out of', len(pmids))
      url = 'https://api.altmetric.com/v1/pmid/'+str(pmid)
      r = requests.get(url)
      time.sleep(1) # rate limit is 1 per sec
      f = pd.json_normalize(r.json())
      Frame = Frame.append(f, ignore_index=True)
    except:
      print("no results")
  if len(Frame) == 0:
    Frame.at[0,'pmid'] = pmid
  return(Frame)
  

def reorder_colmns(df):
  columns = [ 
    "Tool_URL",
    "url_status",
    "Tool_Name",                                                               
    "Tool_Description",
    "PMID",
    "DOI",
    "Article_Title",                                                              
    "Abstract",
    "Author_Information",    
    "Publication_Type",                                                            
    "Grant_List",                                                                 
    "Chemical_List",
    "Citations",
    "Article_Language",                                                         
    "KeywordList",
    "Last_Updated",                                                             
    "Added_On",
    "Published_On",                                                                
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
    "Facebook_Shares"
  ]
    # add columns that are missing
  for col in columns:
    if col not in df.columns:
      df[col]=''
  return(df[columns])
  

if __name__ == '__main__':
  x = api.list_direct_messages()
  # reply to the three latest Directed Messages
  if len(x) == 0 :
    print('No direct messages')
  for message in x:
    print(message)
    # allow only enrichrbot or Avi Maayan to control the bot
    if message.message_create['sender_id'] in ['1146058388452888577','365549634']:
      PMID = message.message_create['message_data']['text']
      api.destroy_direct_message(message.id)
      # collect data
      tool = collect_data(PMID)
      tool = json.dumps(tool)
      tool = json.loads(tool)
      df = pd.json_normalize(tool['MedlineCitation'])
      df = df.astype(str)
      df = create_df(df)
      df = df.reset_index()
      df = pritify(df)
      df = df[pd.notna(df['tool_URL'])]
      df = df[df.astype(str)['tool_URL'] != '[]']
      df['tool_URL'] = keep_first_link(df)
      df = df[~df['tool_URL'].isna()]
      df['tool_URL'] = [ x.replace("..",".") for x in df['tool_URL'] ]
      df = testURL(df) # test if url loads
      df = df.dropna(subset=['tool_URL'])
      df = fix_tool_name(df)
      df['num_citations'] = who_cited(df['PMID'].tolist())
      Altmetric_dataframe = Altmetric(df['PMID'].tolist())
      df = df.merge(Altmetric_dataframe, left_on='PMID', right_on='pmid',how='left')
      meta = pd.read_csv('https://raw.githubusercontent.com/MaayanLab/BioToolStory/master/PubMedTools/CF/data/tool_meta.csv')
      # keep only columns in df
      cl = set(meta['old_name'].tolist()).intersection(df.columns)
      df = df[list(cl)]
      for i in range(0,len(meta)):
        df.rename(columns={meta['old_name'][i]: meta['new_name'][i]}, inplace=True)
      df = reorder_colmns(df)
      df = df[~df['Tool_URL'].isna()]
      df['Tool_URL'] = [ x.replace("..",".") for x in df['Tool_URL'] ]
      df['Tool_Name'] = [ BeautifulSoup(str(x), "lxml").text for x in df['Tool_Name'] ]
      # test tools against bio.tools api
      df = df[pd.notna(df['Abstract'])]
      # clean tool names
      df = df.replace(np.nan, '', regex=True)
      df = df[~df['ISSN'].isna()]
      df = df[df['ISSN']!='']
      df = df[~df['PMID'].isna()]
      df = df[df['PMID'].astype('str')!='']
      df = df[~df['Abstract'].isna()]
      df = df[df['Abstract']!='']
      df["Article_Date"] =  str(datetime.datetime.now().year) + "-01-01"
      df["Year"] =  datetime.datetime.now().year
      df.rename(columns={'Tool_URL':'tool_homepage_url'}, inplace=True)
      # save tools
      s = '1'
      en = '1'
      df.to_csv(os.path.join(PTH,'data/classified_tools_'+s+'_'+en +'.csv'),index=False)
      bashCommand = "python3 /home/maayanlab/Tools/6_pushtools.py 1 1 0"
      process = subprocess.Popen(bashCommand.split(), stdout=subprocess.PIPE)
      output, error = process.communicate()
      
  
