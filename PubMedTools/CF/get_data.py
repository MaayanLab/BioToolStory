# Altmetric json documentaion
# https://docs.google.com/spreadsheets/d/1ndVY8Q2LOaZO_P_HDmSQulagjeUrS250mAL2N5V8GvY/edit#gid=0

from Bio import Entrez
from dotenv import load_dotenv
import pandas as pd
import os
import time
import re, string
import requests
from pandas.io.json import json_normalize
from bs4 import BeautifulSoup
import sys
load_dotenv(verbose=True)

PTH = os.environ.get('PTH')
Entrez.email = os.environ.get('EMAIL')
API_KEY = os.environ.get('API_KEY')

start = str(sys.argv[1])
end = str(sys.argv[2])
s = start.replace("/","")
en = end.replace("/","")

# Articles that cite a given article ONLY covers journals indexed for PubMed Central
# (https://www.ncbi.nlm.nih.gov/pmc/tools/cites-citedby/)
# http://biopython.org/DIST/docs/tutorial/Tutorial.html#htoc137


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


def pritify(df):
  print('pritify...')
  df['Article.ELocationID'] = df['Article.ELocationID'].str.strip("']")
  df['Article.ELocationID'] = df['Article.ELocationID'].str.strip("['")
  df['Article.ELocationID'] = df['Article.ELocationID'].str.strip("['")
  return(df)


def Altmetric(doilist):
  pattern = re.compile(r"[^a-zA-Z0-9-//?.]+")
  i = 0 
  Frame = pd.DataFrame()
  for doi in doilist:
    try:
      doi = pattern.sub('', doi)
      doi = doi.strip(".")
      i = i+1
      print('Altmetric', i, 'out of', len(doilist))
      url = 'https://api.altmetric.com/v1/doi/'+str(doi)
      r = requests.get(url)
      time.sleep(2)
      f = json_normalize(r.json())
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
              #"CF_program",                                                                  
              #"Program Title",
              #"Icon_link",                                                              
              #"Institution",
              #"Project_Number",                                                              
              "PMID",
              #"PMC",                                           
              "DOI",
              "Article_Title",                                                              
              "Abstract",
              "Author_Information",                                                          
              "Electronic_Location_Identifier",
              "Publication_Type",                                                            
              "Copyright_Information",
              "Grant_List",                                                                 
              "Chemical_List",
              "Cited By (PMC_ids)",                                                       
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
              "Mean score for publications",                                              
              #"Mean score for publications in the last 3 month", 
              #"Mean score for publications in this journal",                                 
              #"Mean score for publications in this journal in the last 3 month",
              #"Publications in the last 3 month",                                      
              #"Publications from the last 3 month with fewer mentions" ,
              "Scientists who mentioned  the publication on Twitter",                        
              "News sources that mentioned the publication",
              "Mentions in social media",                                                    
              "Facebook_Shares",
              #"Publications in the last 3 month with fewer mentions",                     
              #"Publications from this journal with fewer mentions",
              #"Altmetric URL" 
    ]
  return(df[columns])

if __name__=='__main__':
  tools = pd.read_csv(os.path.join(PTH,'data/classified_tools_'+s+'_'+en+'.csv'))
  tools = tools[pd.notna(tools['tool_URL'])]
  tools['tool_URL'] = keep_first_link(tools)
  pmc_ids = []
  for i in range(0,len(tools)):
    pubmed_ids = who_cited(str(tools.iloc[i]['PMID']))
    pmc_ids.append(pubmed_ids)
    print('who_cited',i,'out of',len(tools))
  tools['pmc_ids'] = pmc_ids
  tools['num_citations'] = 0
  for i in range(0,len(tools)):
    print(i)
    tools.loc[i,'num_citations'] = len(tools.iloc[i]['pmc_ids'])
  tools = pritify(tools)
  Altmetric_dataframe = Altmetric(tools['Article.ELocationID'].tolist())
  tools['PMID'] = tools['PMID'].astype(str)
  tools['PMID'] = [ pmid.replace('.0','') for pmid in tools['PMID'] ]
  Altmetric_dataframe['pmid'] = Altmetric_dataframe['pmid'].astype('str')
  # merge the Altmetric dataframe with the tools dataframe. Keep all data from tools
  tools1 = tools.merge(Altmetric_dataframe, left_on='PMID', right_on='pmid',how='left')
  meta = pd.read_csv(os.path.join(PTH,"tools_meta.csv"))
  # keep only columns in tools1
  cl = set(meta['old_name'].tolist()).intersection(tools1.columns)
  # reorder columns
  tools1 = tools1[list(cl)]
  # rename columns
  for i in range(0,len(meta)):
    tools1.rename(columns={meta['old_name'][i]: meta['new_name'][i]}, inplace=True)
  # reorder tools names
  tools1 = reorder_colmns(tools1)
  tools1 = tools1[~tools1['Tool_URL'].isna()]
  tools1['Tool_URL'] = [ x.replace("..",".") for x in tools1['Tool_URL'] ]
  tools1['Tool_Name'] = [ BeautifulSoup(str(x), "lxml").text for x in tools1['Tool_Name'] ]
  # save tools
  tools1 = tools1[pd.notna(tools1['Abstract'])]
  tools1.to_csv(os.path.join(PTH,'data/classified_tools_'+s+'_'+en+'_new.csv'),index=None)


