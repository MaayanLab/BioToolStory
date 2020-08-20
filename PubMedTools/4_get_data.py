# Altmetric json documentaion
# https://docs.google.com/spreadsheets/d/1ndVY8Q2LOaZO_P_HDmSQulagjeUrS250mAL2N5V8GvY/edit#gid=0

from Bio import Entrez
from dotenv import load_dotenv
import pandas as pd
import os
import time
import re, string
import requests
from bs4 import BeautifulSoup
import sys
import ast
import numpy as np
from urllib.parse import urlparse
import datetime
from datetime import datetime
import pycountry

load_dotenv(verbose=True)

PTH = os.environ.get('PTH_A')
Entrez.email = os.environ.get('EMAIL')
API_KEY = os.environ.get('API_KEY')

start = str(sys.argv[1])
end = str(sys.argv[2])
s = start.replace("/","")
en = end.replace("/","")

# Articles that cite a given article ONLY covers journals indexed for PubMed Central
# (https://www.ncbi.nlm.nih.gov/pmc/tools/cites-citedby/)
# http://biopython.org/DIST/docs/tutorial/Tutorial.html#htoc137
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


def pritify(df):
  print('pritify...')
  df['Article.ELocationID'] = df['Article.ELocationID'].str.strip("']")
  df['Article.ELocationID'] = df['Article.ELocationID'].str.strip("['")
  df['Article.ELocationID'] = df['Article.ELocationID'].str.strip("['")
  return(df)


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
  return(Frame)


def keep_first_link(df):
  pattern = re.compile(r"[^a-zA-Z0-9-//?.]+")
  links=[]
  # keep only first link
  for i in range(0,len(df)):
    print(i)
    url = df.iloc[i]['tool_URL'].split(",")[0]
    url = url[url.find("http"):]
    index = url.rfind('.')
    url = url[:index+1]+pattern.sub('', url[index:])
    url = url.strip(".")
    links.append(url)
  return(links)


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


def test_tool_name(df):
  df['is_tool'] = 1
  for i in range(len(df)):
      name = df.iloc[i]['Tool_Name']
      print(i)
      url = 'https://bio.tools/api/tool/'+name+'?format=json'
      response = requests.get(url, timeout=20)
      f = response.content
      dict_str = f.decode("UTF-8")
      if not isinstance(dict_str, str):
          mydata = ast.literal_eval(dict_str)
          if mydata['detail'] == 'Not found.':
              df.at[i,'is_tool'] = 0
  return(df)


def clean_tool_name(df):
  df = df[df['Tool_Name'].notna()]
  df = df.reset_index(drop=True)
  for i in range(len(df['Tool_Name'])):
    name = df.iloc[i]['Tool_Name']
    if (len(name) < 3 or len(name) > 20) or ('www' in name) or ('http' in name) or (name.replace(".","").isdigit() or ("." in name)):
      url = df.iloc[i]['Tool_URL']
      if str(url) != 'nan':
        p = urlparse(url)
        p = p.path.strip("/")
        name = p.split("/")[-1]
      else:
        df.at[i,'Tool_Name'] = "NA"
        continue
    if len(name.replace(".","")) > 2:
      for w in ['.jsp','.php','.html','.css','.gz','.gzip','.git','.htm','.zip','.exe', '.js', '.asp','version','.pl','.aspx', '.xls', '.jar','.py']:
        name = name.replace(w,"")
      df.at[i,'Tool_Name'] = name
      for w in ['supplement','english','resource','datalist','software','article']:
        if w in name.lower():
          df.at[i,'Tool_Name'] = "NA"
    else:
      df.at[i,'Tool_Name'] = "NA"
    if len(name) > 30:
      df.at[i,'Tool_Name'] = "NA"
    for w in ['dna','rna',]:
      if w == name.lower():
        df.at[i,'Tool_Name'] = "NA"
  df = df[df['Tool_Name']!="NA"]
  return(df)
  

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


def get_country(author_list):
  countries = []
  country_names = [country.name.lower() for country in pycountry.countries ]
  country_names.append("usa")
  country_names.append('Korea')
  country_names.append(' uk ')
  country_names.append(' uk.')
  country_names.append('United Arab Emirates')
  country_names.append('Saudi Arabia')
  country_names.append('Taiwan')
  for affil in author_list:
    text = str(affil)
    country = [country for country in country_names if country in text.lower()]
    if len(country) > 0:
      countries.append(country[0])
    else:
      countries.append('')
  countries=[c.replace(".","") for c in countries]
  countries = [ c.strip() for c in countries ]
  countries=[c.capitalize() for c in countries]
  for i in range(len(countries)):
    if countries[i].lower() in ["usa", " uk ", " uk"]:
      countries[i] = countries[i].upper()
    if countries[i].lower() == "united kingdom" or countries[i].lower() == "uk":
      countries[i] = "UK"
    if countries[i].lower() == "united states":
      countries[i] = "USA"
  return(countries)


def read_data(fpath):  
  try:
    return(pd.read_csv(fpath,dtype=str))
  except:
    print("No tools were detected for",start)
    sys.exit()


if __name__=='__main__':
  # laod tools
  tools = read_data(os.path.join(PTH,'data/classified_tools_'+s+'_'+en+'.csv'))
  tools = tools[pd.notna(tools['tool_URL'])]
  tools['tool_URL'] = keep_first_link(tools)
  tools['num_citations'] = who_cited(tools['PMID'].tolist())
  tools = pritify(tools)
  Altmetric_dataframe = Altmetric(tools['PMID'].tolist())
  tools['PMID'] = tools['PMID'].astype(str)
  tools['PMID'] = [ pmid.replace('.0','') for pmid in tools['PMID'] ]
  Altmetric_dataframe['pmid'] = Altmetric_dataframe['pmid'].astype('str')
  # merge the Altmetric dataframe with the tools dataframe. Keep all data from tools
  tools1 = tools.merge(Altmetric_dataframe, left_on='PMID', right_on='pmid',how='left')
  # https://raw.githubusercontent.com/MaayanLab/BioToolStory/master/PubMedTools/CF/data/tool_meta.csv?token=AFKKUELTKW324YQPDO22AXK7GF4YY
  meta = pd.read_csv('https://raw.githubusercontent.com/MaayanLab/BioToolStory/master/PubMedTools/CF/data/tool_meta.csv')
  # keep only columns in tools1
  cl = set(meta['old_name'].tolist()).intersection(tools1.columns)
  # reorder columns
  tools1 = tools1[list(cl)]
  # rename columns!!!!!
  for i in range(0,len(meta)):
    tools1.rename(columns={meta['old_name'][i]: meta['new_name'][i]}, inplace=True)
  # reorder tools names
  tools1 = reorder_colmns(tools1)
  tools1 = tools1[~tools1['Tool_URL'].isna()]
  tools1['Tool_URL'] = [ x.replace("..",".") for x in tools1['Tool_URL'] ]
  tools1['Tool_Name'] = [ BeautifulSoup(str(x), "lxml").text for x in tools1['Tool_Name'] ]
  # test tools against bio.tools api
  tools1 = test_tool_name(tools1)
  tools1 = tools1[pd.notna(tools1['Abstract'])]
  # clean tool names
  tools1 = tools1.replace(np.nan, '', regex=True)
  tools1 = remove_tools(tools1)
  tools1 = tools1[~tools1['ISSN'].isna()]
  tools1 = tools1[tools1['ISSN']!='']
  tools1 = tools1[~tools1['PMID'].isna()]
  tools1 = tools1[tools1['PMID'].astype('str')!='']
  tools1 = tools1[~tools1['Abstract'].isna()]
  tools1 = tools1[tools1['Abstract']!='']
  tools1 = clean_tool_name(tools1)
  tools1["Country"] = get_country(tools1["Author_Information"])
  tools1["Article_Date"] =  start.replace("/","-")
  tools1["Year"] = datetime.today().strftime('%Y')
  tools1.rename(columns={'Tool_URL':'tool_homepage_url'}, inplace=True)
  # save tools
  tools1.to_csv(os.path.join(PTH,'data/classified_tools_'+s+'_'+en+'.csv'),index=False)
  

