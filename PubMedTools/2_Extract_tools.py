# read pubmed json of articles that have like in their title or abstract and extract tool name and description using a rule and NER.
# save data to file data/tools.csv

import os
from Bio import Entrez
import spacy
from spacy import displacy
from spacy.tokens import Span
from collections import Counter
import en_core_web_sm
nlp = en_core_web_sm.load()
import json
import os.path
from itertools import groupby
import re
import string
import nltk
from nltk.corpus import stopwords
import pandas as pd
from dotenv import load_dotenv
from bs4 import BeautifulSoup
import sys
import gzip

nltk.download('stopwords')

load_dotenv(verbose=True)

start = str(sys.argv[1])
end = str(sys.argv[2])
s = start.replace("/","")
en = end.replace("/","")
stop_words = set(stopwords.words('english'))
stop_words.update(set(["one","two","three","four","five","six","seven","nine","ten","zero"]))
PTH = os.environ.get('PTH_A') # PTH = "/home/maayanlab/Tools/"
Entrez.email = os.environ.get('EMAIL')
API_KEY = os.environ.get('API_KEY')

keeplist = '=./_:-' #characters to keep in url

# read a list of keywords to ignore
f = open(os.path.join(PTH,'RemoveKeyWords.txt'), 'r')
blacklist = f.readlines()
blacklist = [x.rstrip('\n') for x in blacklist]
f.close()


def remove_stop_words(text_list):
  filtered_sentence = [w for w in text_list if not w.lower() in stop_words]
  return(filtered_sentence)


def getEntity(title,abstract):
  URL = re.findall("(?P<url>https?://[^\s]+)", abstract)
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
  text = title
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
 

if __name__=='__main__':
  Frame = pd.DataFrame()
  filesnames = [ x for x in os.listdir(os.path.join(PTH,'data/tools_'+s+'_'+en)) if x.endswith("json.gz")]
  i = 0 
  tot = len(filesnames)
  for file in filesnames:
    print(i,'out of', tot)
    i=i+1
    with gzip.open(os.path.join(PTH,'data/tools_'+s+'_'+en,file)) as fin:
      try:
        json_obj = json.load(fin)
        df = pd.json_normalize(json_obj['MedlineCitation'])
        article = json_obj['MedlineCitation']
        PMID = is_key(['PMID'],article)
        ArticleTitle = is_key(['Article','ArticleTitle'],article)
        AbstractText = str(article['Article']['Abstract'])
        data = getEntity(ArticleTitle,AbstractText)
        if data=='': # no valid links in the paper
          continue
        df['tool_name'] = [data[0]]
        df['tool_description'] = data[1]
        df['tool_URL'] = [data[2]]
        Frame = Frame.append(pd.DataFrame(data = df), ignore_index=True)
      except Exception as e:
        print(e,'at line 186',i,'out of', tot)
  Frame.to_csv(os.path.join(PTH,'data/tools_'+s+'_'+en+'.csv'), index=False) # write tools dataframe to file
