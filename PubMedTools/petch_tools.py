# Tables: resources <program,uuid> --> libraries <journal,ISSN> --> signatures <tools,pmid>


# to start the sigcom server do:
#2. cd /users/alon/desktop/github/signature-commons/
#3. npm start

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
import collections
import ast
from datetime import datetime
from itertools import chain
import math
  
load_dotenv(verbose=True)

PTH = os.environ.get('PTH_A')

API_url = os.environ.get('API_URL')
username = os.getenv("USERNAME")
password = os.getenv("PASSWORD")
credentials = HTTPBasicAuth(username, password)

start = str(sys.argv[1])
end = str(sys.argv[2])
s = start.replace("/","")
en = end.replace("/","")

# delete a journal
# res = requests.delete(API_url%('libraries','b788c70e-79af-4acc-8ccf-0816c7bb59e3', auth=credentials)

# delete a single item
def delete_data(data,schema):
  res = requests.delete(API_url%(schema,data["id"]), auth=credentials)
  if not res.ok:
    raise Exception(res.text)


# delete all * from Database
def del_all_tools(schema):
  res = requests.get(API_url%(schema,""))
  tools_DB = res.json()
  for tool in tools_DB:
    delete_data(tool,schema)


# dump json to file
def write_to_file(schema):
  res = requests.get(API_url%(schema,""))
  tools_DB = res.json()
  with open(os.path.join(PTH,schema + '.json'), 'w') as outfile:
    json.dump(tools_DB, outfile)


def post_data(data,model):
  time.sleep(1)
  res = requests.post(API_url%(model,""), auth=credentials, json=data)
  try:
    if not res.ok:
      raise Exception(res.text)
  except Exception as e:
    print(e)
    f = open(os.path.join(PTH,"data/fail_to_load.txt"), "a")
    f.write(','.join(map(str, data['meta']['PMID'])) + "\n")
    f.close()


# # fix pubmed json 
def fix_dirty_json(text,flg=False):
  if isinstance(text, pd.Series):
    text = text.tolist()[0]
  if isinstance(text, list):
    return(text)
  try:
    x = ast.literal_eval(text)
  except:
    if(flg):
      x = text
    else:
      x = []
  return(x)
  

def find_max(duplicates):
  mx = duplicates[0]
  mn_date = 'None'
  if 'Article_Date' in mx['meta']:
    mx_date = datetime.strptime(mx['meta']['Article_Date'], '%m-%d-%Y')
    for tool in duplicates:
      try:
        dt = datetime.strptime(tool['meta']['Article_Date'], '%Y-%m-%d')
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
              "last_author_country",
             # "Electronic_Location_Identifier",
              "Publication_Type",                                                            
              "Grant_List",                                                                 
              "Chemical_List",
              #"Citations",
              "Article_Language",                                                         
              "KeywordList",
              "Last_Updated",                                                             
              "Added_On",
              "Published_On",                                                                
              #"Article_Date",
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
  df = df[columns]
  df.rename(columns={'last_author_country':'Author_Country'}, inplace=True)
  return(df)


def push_new_journal(ISSN):
  try:
    time.sleep(1)
    url = 'http://api.crossref.org/journals/' + urllib.parse.quote(ISSN)
    resp = req.get(url)
    text = resp.text
    resp = json.loads(text)
    jour = resp['message']['title'] #journal name
    pub = resp['message']['publisher']
  except Exception as e:
    print("error in push_new_journal() --> ", e)
    jour = 'NA'
    pub = 'NA'
  new_journal = {'$validator': '/dcic/signature-commons-schema/v5/core/library.json', 
  'id': str(uuid.uuid4()),
  'dataset': 'journal',
  'dataset_type': 'rank_matrix', 
  'meta': {
    'Journal_Title': jour,
    'ISSN': ISSN,
    'publisher': pub,
    'icon': '',
    # replace validator with raw.github
    '$validator': 'https://raw.githubusercontent.com/MaayanLab/btools-ui/toolstory/validators/btools_journal.json', 
    }
    }
  new_journal = empty_cleaner(new_journal)
  post_data(new_journal,"libraries")
  return(new_journal['id'])


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


def read_journals():
  res = requests.get(API_url%("libraries",""))
  journals_DB = res.json()
  ISSNs = [ [x['meta']['eISSN'], x['id']] for x in journals_DB if 'eISSN' in x['meta'].keys() ]
  ISSNs = pd.DataFrame(ISSNs,columns=['ISSN','key']) # ISSN and table key
  return(ISSNs)
  
  
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
  
  
def rename2(df):
  del df['medlinejournalinfo.country']
  del df['data']
  del df['stat']
  del df['X.validator']
  del df['id']
  del df['library']
  del df['meta..validator']
  del df['meta.Electronic_Location_Identifier']
  del df['meta.Citations']
  del df['Readers_Count']
  del df['Readers.in.Mendeley']
  del df['Readers.in.Connotea']
  del df['Readers.in.Citeulike']
  del df['Cited_By_Posts_Count']
  del df['Twitter.accounts.that.tweeted.this.publication']
  del df['Users.who.ve.mentioned.the.publication.on.Twitter']
  del df['Mean.score.for.publications']
  del df['Scientists.who.mentioned..the.publication.on.Twitter']
  del df['News.sources.that.mentioned.the.publication']
  del df['Mentions.in.social.media']
  del df['Facebook_Shares']
  del df['last_author']
  del df['first_author']
  del df['pmc2pmid']
  del df['meta.Article_Date']
  df.columns = ['PMID','Abstract','Article_Title',  'Author_Information','DOI',
                'Grant_List', 'Journal', 'ISSN','Journal_Title','Article_Language','Chemical_List',
                'Published_On', 'KeywordList', 'Tool_Description','Tool_URL', 'Tool_Name', 'url_status', 
                'Added_On','Last_Updated','Readers_Count','Altmetric_Score','Publication_Type',
                'Readers_in_Mendeley', 'Cited_By_Posts_Count', 'Mentions_in_social_media',
                'Twitter_accounts_that_tweeted_this_publication', 'Users_who_mentioned_the_publication_on_Twitter',
                'Scientists_who_mentioned_the_publication_on_Twitter','Facebook_Shares',
                'News_sources_that_mentioned_the_publication',
                'Readers_in_Citeulike', 'Readers_in_Connotea', 'Publicaions_in_this_journal',
                'last_author_country',
                'Cited (By PMC_ids)'
                ]
  return(df)


def clean_tool_name(df):
  from urllib.parse import urlparse
  df = df[df['Tool_Name'].notna()]
  df = df.reset_index(drop=True)
  for i in range(len(df['Tool_Name'])):
    name = df.iloc[i]['Tool_Name']
    if (len(name) < 3 or len(name) > 20) or ('www' in name) or ('http' in name) or (name.replace(".","").isdigit() or ("." in name)):
      url = df.iloc[i]['tool_homepage_url']
      p = urlparse(url)
      p = p.path.strip("/")
      name = p.split("/")[-1]
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


def get_country(author_list):
  text = str(author_list)
  country = [country.name for country in pycountry.countries if country.name.lower() in text.lower()]
  if len(country) > 0:
    return(country[0])
  else:
    return("")

  
def push_tools(df):
  df = df.replace(np.nan, '', regex=True)
  df = remove_tools(df)
  df = rename(df)
  df = reorder_colmns(df)
  # test for ISSN
  df = df[~df['ISSN'].isna()]
  df = df[df['ISSN']!='']
  # test for PMID
  df = df[~df['PMID'].isna()]
  df = df[df['PMID']!='']
  # test for Abstract
  df = df[~df['Abstract'].isna()]
  df = df[df['Abstract']!='']
  df.rename(columns={'Tool_URL':'tool_homepage_url'}, inplace=True)
  df = clean_tool_name(df)
  k = len(df)
  i = 0
  keep = df.columns.drop(['Author_Information','Article_Date'])
  for tool in df.to_dict(orient='records')[0:]:
    print('Uploaded',i,'tools out of',k)
    i = i + 1
    data = {}
    data["$validator"] = '/dcic/signature-commons-schema/v5/core/signature.json'
    data["id"] = str(uuid.uuid4()) # create random id
    ISSN = tool['ISSN']
    # get journals from DB
    res = requests.get(API_url%("libraries",""))
    journal_list = res.json()
    key = [x['id'] for x in journal_list if x['meta']['ISSN']==ISSN ]
    if len(key)>0:
      data["library"] = key[0] # uuid from libraries TABLE
    else:
      data["library"]  = push_new_journal(ISSN)
    data["meta"] = { key: tool[key] for key in keep }
    data["meta"]["PMID"] = [data["meta"]["PMID"]]
    data["meta"]["Author_Information"] = fix_dirty_json(tool['Author_Information'])
    data["meta"]["Country"] = get_country(data["meta"]["Author_Information"])
    x=tool['Published_On']
    data["meta"]["Article_Date"] =  "01" + "-" + "01" + "-" + str(x)  #------------------>
    data["meta"]["Abstract"] =  fix_dirty_json(tool['Abstract'],flg=True)
    if data["meta"]["Abstract"] == '': # this is a mandatory field
      print("missing abstract")
      continue
    data["meta"]["Article_Language"] =  fix_dirty_json(tool['Article_Language'])
    data["meta"]["Electronic_Location_Identifier"] =  str(fix_dirty_json(tool['DOI']))
    data["meta"]["Publication_Type"] =  fix_dirty_json(tool['Publication_Type'])
    data["meta"]["Grant_List"] =  fix_dirty_json(tool['Grant_List'])
    data["meta"]["Chemical_List"] =  fix_dirty_json(tool['Chemical_List'])
    data["meta"]["KeywordList"] =  fix_dirty_json(tool['KeywordList'])
    if len(data["meta"]["KeywordList"]) >0:
      if isinstance(data["meta"]["KeywordList"], list):
        data["meta"]["KeywordList"] = data["meta"]["KeywordList"][0]
    data["meta"]["Last_Updated"] = to_human_time(data["meta"]["Last_Updated"])
    data["meta"]["Added_On"] = to_human_time(tool['Added_On'])
    data["meta"]["Published_On"] = to_human_time(tool['Published_On'])
    data["meta"]["$validator"] = 'https://raw.githubusercontent.com/MaayanLab/btools-ui/toolstory/validators/btools_tools.json'
    data["meta"] = empty_cleaner(data['meta']) # delete empty fields
    post_data(data,"signatures")


if __name__ == "__main__":
  if os.path.exists(os.path.join(PTH,"data/fail_to_load.txt")):
    os.remove(os.path.join(PTH,"data/fail_to_load.txt")) # delete failure log file
  onlyfiles = os.listdir(os.path.join(PTH,'data/'))
  onlyfiles = [ x for x in onlyfiles if ".csv" in x]
  df = pd.read_csv(os.path.join(PTH,'data',onlyfiles[0]))
  for file in onlyfiles[1:]:
    df = pd.concat([df, pd.read_csv(os.path.join(PTH,'data',file))])
  push_tools(df)
  combine_duplicates_tools()
  

# load tools and push them to btools
df = pd.read_csv("/users/alon/desktop/tools_2000_2019_4.csv")
df = df[df['data']=='old']
df = rename2(df)
push_tools(df)

# load json dump into a dataframe
import pandas as pd
import json
from pandas.io.json import json_normalize

patients_df = pd.read_json('/users/alon/desktop/github/btools/PubmedTools/signatures.json')
patients_df = patients_df['meta']
df = pd.json_normalize(patients_df)
df.to_csv('/users/alon/desktop/tools_2000_2019_5.csv',index=False)


#-------------------------- update query for tools --------------------------

# read data
df = pd.read_csv("/users/alon/desktop/tools_6.csv")
# concatinate author names
for i in range(len(df)):
  print(i)
  try:
    authors = fix_dirty_json(df.iloc[i]['Author_Information'])
    tmp = ''
    for author in authors:
      if tmp!='': 
        tmp = tmp + " & "
      tmp=tmp+author['ForeName'] +' '+ author['LastName']
    df.at[i,'FullNames'] = tmp
  except Exception as e:
    print(e)
df.to_csv("/users/alon/desktop/tools_6.csv",index=False)



def isnan(x):
  if type(x) == str:
    if x=='nan':
      return('')
    return(x)
  if math.isnan(x):
    return('')
  else:
    return(x)


# read data from dataframe
df = pd.read_csv("/users/alon/desktop/tools_6.csv")
df = df.replace(np.nan, '', regex=True)
# read data from ToolStory
res = requests.get(API_url%('signatures',""))
tools_DB = res.json()
topic_vec = pd.read_csv('/users/alon/desktop/topics.tsv',sep="\t") # read topics
i = 0
for tool in tools_DB[0:]:
  print(i)
  i=i+1
  # keep only tools in tools_6
  id = tool['id']
  if len(df[ str(tool['meta']['PMID']) == df['PMID']])>0:
    dt = pd.DataFrame({ 'Topic_name':[
                                  'Genome sequence databases',
                                  'Alignment algorithms and methods',
                                  'Tools to perform sequence analysis',
                                  'Sequence-based prediction of DNA and RNA',
                                  'Disease study using gene expression',
                                  'Protein structure',
                                  'Biological pathways and interactions',
                                  'Drugs and chemical studies',
                                  'Brain studies using images'
                                  ],
                      'LDA_probability': topic_vec[topic_vec['id']==id].iloc[:,2:11].values.tolist()[0],
                      'Topic_number': ['1','2','3','4','5','6','7','8','9']
                    })
    dt = dt.sort_values('LDA_probability',ascending=False)
    #dt['LDA_probability'] = dt['LDA_probability'].astype(str)
    dt.reset_index().to_json(orient='records')
    js=dt.to_json(orient='records')
    tool['meta']['Topic'] = ast.literal_eval(js)
    # Have a field for just the year --> year
    tool['meta']['year'] = isnan(df[str(tool['meta']['PMID']) == df['PMID']]['year'].tolist()[0])
    # fix country data
    tool['meta']['Country'] = isnan(df[ str(tool['meta']['PMID']) == df['PMID'] ]['Country'].tolist()[0])
    # concatenate the first name + last name of the authors --> FullNames
    tool['meta']['FullNames'] = isnan(df[ str(tool['meta']['PMID']) == df['PMID'] ]['FullNames'].tolist()[0])
    # institution of the last author
    tool['meta']['Institution'] = isnan(df[str(tool['meta']['PMID']) == df['PMID'] ]['institute'].tolist()[0])
    tool['meta']['institution'] = ''
    tool['meta']['Topic'] = ''
    # set tool name
    tool['meta']['Tool_Name'] = isnan(df[str(tool['meta']['PMID']) == df['PMID'] ]['Tool_Name'].tolist()[0])
    # delete empty fields
    tool["meta"] = empty_cleaner(tool['meta'])
    # push the tool back
    res = requests.patch('https://amp.pharm.mssm.edu/toolstory/meta-api/' +"signatures/" + tool['id'], json=tool, auth=credentials)
    if not res.ok:
      print(res.text)
      break
  else:
    print(tool['meta']['PMID'])
    #delete_data(tool,'signatures')
# add data to validator

#-----------------------------------------------------------
# itterate over journals and update journal name by ISSN
df = pd.read_csv("/users/alon/desktop/tools_6.csv")
df = df.replace(np.nan, '', regex=True)

res = requests.get(API_url%('libraries',""))
journal_DB = res.json()
for jour in journal_DB:
  if jour['meta']['Journal_Title']=='NA':
    print(jour['meta']['ISSN'])
    if len(df[ df['ISSN']==jour['meta']['ISSN'] ])>0:
      jour['meta']['Journal_Title'] = df[ df['ISSN']==jour['meta']['ISSN'] ]['Journal_Title'].tolist()[0]
      res = requests.patch('https://amp.pharm.mssm.edu/toolstory/meta-api/' +"libraries/" + jour['id'], json=jour, auth=credentials)
      if not res.ok:
        print(jour)
        print(res.text)
        break

PMIDs = df['PMID'].tolist()


# update the website after petching data
res = requests.get("https://amp.pharm.mssm.edu/toolstory/meta-api/optimize/refresh", auth=credentials)
print(res.ok)
res = requests.get("https://amp.pharm.mssm.edu/toolstory/meta-api/"+"optimize/status", auth=credentials)
while not res.text == "Ready":
    time.sleep(1)
    res = requests.get("https://amp.pharm.mssm.edu/toolstory/meta-api"+"/optimize/status", auth=credentials)
res = requests.get("https://amp.pharm.mssm.edu/toolstory/meta-api/"+"summary/refresh", auth=credentials)
print(res.ok)