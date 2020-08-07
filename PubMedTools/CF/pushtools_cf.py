# Guidlines in: https://github.com/MaayanLab/Sigcom-Tutorial/blob/master/Customizing%20Signature%20Commons.ipynb

import requests
import urllib.request
import json
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
import openpyxl
import ast

# TBLs: resources <program,uuid> --> libraries <project,project.number> --> signatures <tools,pmid>
  
load_dotenv(verbose=True)

API_url = os.environ.get('API_URL')
credentials=HTTPBasicAuth('signaturestore','signaturestore')
PTH = os.environ.get('PTH')


def delete_data(data,model):
  res = requests.delete(API_url%(model,data["id"]), auth=credentials)
  if not res.ok:
    raise Exception(res.text)


# delete all * from Database
def del_all(schema):
  res = requests.get(API_url%(schema,""))
  tools_DB = res.json()
  for tool in tools_DB:
    delete_data(tool,schema)
  

def write_to_file(schema):
  res = requests.get(API_url%(schema,""))
  tools_DB = res.json()
  with open(os.path.join(PTH,schema + '.txt'), 'w') as outfile:
    json.dump(tools_DB, outfile)
  

def post_data(data,model):
  res = requests.post(API_url%(model,""), auth=credentials, json=data)
  if not res.ok:
    raise Exception(res.text)

  
# # fix pubmed json 
def fix_dirty_json(text):
  try:
    x = ast.literal_eval(text)
  except:
    x = ""
  return(x)

 
def reorder_colmns(df):
  columns = [ 
              "Tool_URL",
              #"status",
              "Tool_Name",                                                               
              "Tool_Description",
              "CF_program",                                                                  
              "Program Title",
              "Icon_link",                                                              
              "Institution",
              "Project_Number",                                                              
              "PMID",
              #"PMC",                                           
              "DOI",
              "Article_Title",                                                              
              "Abstract",
              "Author_Information",                                                          
              "Electronic_Location_Identifier",
              "Publication_Type",                                                            
              #"Copyright_Information",
              "Grant_List",                                                                 
              "Chemical_List",
              #"Cited By (PMC_ids)",                                                       
              "Citations",
              "Article_Language",                                                         
              "KeywordList",
              "Last_Updated",                                                             
              "Added_On",
              #"Date_Revised_Month",                                                       
              #"Date_Revised_Day",
              #"Date_Revised_Year"  ,                                                         
              #"Date_Completed_Day",
              #"Date_Completed_Month",                                                        
              #"Date_Completed_Year",
              "Published_On",                                                                
              "Article_Date",
              "Journal",                                                                     
              "ISSN",
              "Journal_Title",                                                               
              #"Journal_ISO_Abbreviation",
              #"Publisher_Subjects",                                                         
              #"Journal_Issue",
              #"Journal_Issue_Volume",                                                       
              #"Journal_Issue_PubDate_Day",
              #"Journal_Issue_PubDate_Month",                                                 
              #"Journal_Issue_PubDate_Year",
              #"Medline_Journal_Info",                                                        
              #"MEDLINE_ID",
              #"Medline_Journal_Info_Country",                                                
              #"Medline_Journal_Info_ISSN_Linking",
              #"Pagination_Medline",                                                          
              #"Mesh_Heading_List",
              #"Altmetric_ID",                                                              
              "Altmetric_Score",
              #"Altmetric_Journal_ID",                                                      
              "Publicaions in this journal",
              #"Publications in this journal in the last 3 month",                           
              #"Publications in the last 3 month...55",
              #"Altmetric's score in context rank within publications in the journal",        
              "Readers_Count",
              "Readers in Mendeley",                                                         
              "Readers in Connotea",
              "Readers in Citeulike",                                                        
              "Cited_By_Posts_Count",
              "Twitter accounts that tweeted this publication",                         
              "Users who've mentioned the publication on Twitter",
              #"Publications with fewer mentions",                                      
              #"% publications from this journal with fewer mentions",
              #"% publications from this journal with fewer mentions in the last 3 month", 
              #"Score in context rank within publications in the last 3 month",
              #"Score in context rank within publications in the journal",                   
              #"Score in context rank within publications in the journal in the last 3 month",
              #"Mean score for publications",                                              
              #"Mean score for publications in the last 3 month", 
              #"Mean score for publications in this journal",                                 
              #"Mean score for publications in this journal in the last 3 month",
              #"Publications in the last 3 month",                                      
              #"Publications from the last 3 month with fewer mentions",
              "Scientists who mentioned  the publication on Twitter",                        
              "News sources that mentioned the publication",
              "Mentions in social media",                                                    
              "Facebook_Shares",
              #"Publications in the last 3 month with fewer mentions",                     
              #"Publications from this journal with fewer mentions",
              #"Altmetric URL" 
    ]
  return(df[columns])


def combine_duplicates_tools():
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
  for i in range(6,len(tools_DB)):
    print(i)
    url = tools_DB[i]['meta']['tool_homepage_url']
    duplicates = [ x for x in tools_DB if url == x['meta']['tool_homepage_url'] ]
    if len(duplicates)>1: # if more than one tool with the same url
      row = duplicates[0] # keep the first row
      citations = 0
      pmids = []
      for k in range(0,len(duplicates)):
        if type(duplicates[k]['meta']['PMID']) != list: 
          pmids.append(duplicates[k]['meta']['PMID'])
        else:
          unlist(duplicates[k]['meta']['PMID'])
        delete_data(duplicates[k],'signatures')
      if duplicates[k]['meta']['Citations'] == None:
        duplicates[k]['meta']['Citations'] = 0
      citations = citations + duplicates[k]['meta']['Citations']
      row['meta']['PMID'] = list(set(pmids))
      row['meta']['Citations'] = citations
      post_data(row,"signatures")


def push_tools():
  # get project ids
  res = requests.get(API_url%("libraries",""))
  project_DB = res.json()
  pids = [ [x['meta']['pid'], x['id']] for x in project_DB ]
  pids = pd.DataFrame(pids,columns=['pid','key']) # ISSN and table key
  # read new tools
  df = pd.read_excel(os.path.join(PTH,'data/tools_new.xlsx'),skiprows=1)
  df = df.replace(np.nan, '', regex=True)
  # rename column
  df = reorder_colmns(df)
  df.rename(columns={'Tool_URL':'tool_homepage_url'}, inplace=True)
  # push new tools to the database
  k = len(df)
  i = 0
  keep = df.columns.drop(['Project_Number','Author_Information','Grant_List','Article_Date'])
  for tool in df.to_dict(orient='records'):
    print('Uploaded',i,'tools out of',k)
    data = {}
    data["$validator"] = '/dcic/signature-commons-schema/v5/core/signature.json'
    data["id"] = str(uuid.uuid4()) # create random id
    pid_t = tool['Project_Number']
    key = pids[pids['pid']==pid_t]['key'].tolist()[0]
    data["library"] = key # uuid from libraries TABLE
    data["meta"] = { key: tool[key] for key in keep }
    data["meta"]["Author_Information"] = fix_dirty_json(tool['Author_Information'])
    data["meta"]["Grant_List"] = fix_dirty_json(tool['Grant_List'])
    data["meta"]["Article_Date"] =  fix_dirty_json(tool['Article_Date'])
    data["meta"]["Abstract"] =  fix_dirty_json(tool['Abstract'])
    data["meta"]["Article_Language"] =  fix_dirty_json(tool['Article_Language'])
    data["meta"]["Electronic_Location_Identifier"] =  fix_dirty_json(tool['Electronic_Location_Identifier'])
    data["meta"]["Publication_Type"] =  'Journal'
    data["meta"]["$validator"] = '/dcic/signature-commons-schema/v5/core/unknown.json'
    i = i + 1
    post_data(data,"signatures")
  combine_duplicates_tools()
  print("Done updating new tools")


def push_project():
  # get program ids
  i = 0
  res = requests.get(API_url%("resources",""))
  program_DB = res.json()
  pnums = [ [x['meta']['CF_program'], x['id']] for x in program_DB ]
  pnums = pd.DataFrame(pnums,columns=['CF_program','id']) # ISSN and table key
  df = pd.read_csv(os.path.join(PTH,'data/projects.csv'),dtype=str)
  # push new journals to DB
  for proj in df.to_dict(orient='records'):
    data = {
    "$validator": '/dcic/signature-commons-schema/v5/core/library.json',
    "id" :  str(uuid.uuid4()),
    "resource": pnums[pnums['CF_program']==proj['CF_program']].id.tolist()[0],
    "dataset": "project",
    "dataset_type" : "rank_matrix",
    "meta":{
      "pid" :  proj['Project number'],
      'name' : proj['PI'],
      'Institution': proj['Institution'],
      'Title': proj['Title'],
      'CF_program': proj['CF_program'],
      'pnum': proj['pnum'],
      '$validator': "/@dcic/signature-commons-schema/core/unknown.json"
      }
    }
    data = json.dumps(data)
    post_data(data,"libraries")
    print(i)
    i = i + 1
  print("Done updating new projects")


def push_programs():
  df = pd.read_csv(os.path.join(PTH,'data/programs.csv'))
  # create uuid
  for prog in df.to_dict(orient='records'):
    data = {}
    data["id"] = str(uuid.uuid4())
    data["meta"] = prog
    data["meta"]["$validator"] = "/@dcic/signature-commons-schema/core/unknown.json"
    post_data(data,"resources")
  print("Done updating new programs")

  
if __name__ == "__main__":
  push_journals() # update journals
  push_tools()
  

