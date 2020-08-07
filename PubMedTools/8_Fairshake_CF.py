import rdflib
import pandas as pd
import requests
import os
import traceback as tb
import time
from difflib import SequenceMatcher
from googlesearch import search #pip3 install google
import coreapi
from dotenv import load_dotenv
from os import listdir
from os.path import isfile, join

load_dotenv(verbose=True)

PTH = os.environ.get('PTH_A')

# FAIRshake account
Fair_api_key = os.environ.get('Fair_api_key')
client = coreapi.Client(auth=coreapi.auth.TokenAuthentication(token=api_key, scheme='token'))

# help function
def save_to_file(file):
  df.to_csv('/users/alon/desktop/FAIR.csv',index=None)


# Fair Questions
def FAIRshakeit(df,file):
  #-------------------------------------------------------------------------------------------------------------------------------------
  # 1) Machine readable metadata
  # tested with API from https://rdf-translator.appspot.com/
  #-------------------------------------------------------------------------------------------------------------------------------------
  df['Machine_readable_metadata'] = 0
  for i in range(0,len(df)):
    print(i)
    url = df.iloc[i]['meta.tool_homepage_url']
    g = rdflib.Graph()
    try:
      result = g.parse(url)
      if len(g)>1:
        df.at[i,'Machine_readable_metadata'] = 1
    except:
      pass
  save_to_file(file)
  print('Assessment 1 is done')
  #-------------------------------------------------------------------------------------------------------------------------------------
  # 2) Persistent identifier - Does the tool contains DOI?
  # A standardized ID or accession number is used to identify the dataset
  #-------------------------------------------------------------------------------------------------------------------------------------
  df = pd.read_csv(os.path.join(PTH,"data",file))
  df['Does_the_tool_contains_DOI'] = 0
  for i in range(0,len(df)):
    print(i)
    doi = df.iloc[i]['meta.Electronic_Location_Identifier']
    if doi == '[]':
      df.at[i,'Does_the_tool_contains_DOI']  = 0
    else:
      df.at[i,'Does_the_tool_contains_DOI']  = 1
  save_to_file(file)
  print('Assessment 2 is done')
  #-------------------------------------------------------------------------------------------------------------------------------------
  # 3) The tool can be freely downloaded or accessed from a webpage
  # Globally unique identifier - tool_url_is_active?
  #-------------------------------------------------------------------------------------------------------------------------------------
  df = pd.read_csv(os.path.join(PTH,"data",file))
  df['tool_url_is_active'] = 0
  for i in range(0,len(df['meta.tool_homepage_url'])):
    url = df.iloc[i]['meta.tool_homepage_url']
    try:
      request = requests.head(url,allow_redirects=False, timeout=5)
      status = request.status_code
      df.at[i,'tool_url_is_active'] = str(status)
    except:
      pass
  df['tool_url_is_active'] = df['tool_url_is_active'].isin([200,202,203,301,302,308]).astype(int)
  save_to_file(file)
  print('Assessment 3 is done')
  #-------------------------------------------------------------------------------------------------------------------------------------
  # 4) Resource discovery through web search - the tool has a unique_name? *
  # The tool has a unique name and an informative description 
  #-------------------------------------------------------------------------------------------------------------------------------------
  # search google for the tool name --> if the link is in the first 10 results --> the tool gets a full score
  df = pd.read_csv(os.path.join(PTH,"data",file))
  df['unique_name'] = 0
  for i in range(0,len(df['meta.Tool_Name'])):
    tool  =  df.iloc[i]['meta.Tool_Name']
    for res in search(tool,        # The query you want to run
                  tld = 'com',  # The top level domain
                  lang = 'en',  # The language
                  num = 10,     # Number of results per page
                  start = 0,    # First result to retrieve
                  stop = 10,  # Last result to retrieve
                  pause = 2.0,  # Lapse between HTTP requests
                 ):
      if (SequenceMatcher(None, res, df.iloc[i]['meta.tool_homepage_url']).ratio()) > 0.95:
        df.at[i,'unique_name'] = 1
        break
    print(i)
    time.sleep(1)
  df.loc[df['unique_name'].isna(),'unique_name'] = 0
  save_to_file(file)
  print('Assessment 4 is done')
  #-------------------------------------------------------------------------------------------------------------------------------------
  # 5) Open, Free, Standardized Access protocol
  # The tool can be accessed programmatically through an API and follows community standards for open APIs
  #-------------------------------------------------------------------------------------------------------------------------------------
  df = pd.read_csv(os.path.join(PTH,"data",file))
  df.loc[df['meta.tool_homepage_url']==url,'API'] = 0
  for url in df['meta.tool_homepage_url']:
    try:
      r = requests.get(url,allow_redirects=True, timeout=5)
      request = requests.head(url,allow_redirects=False, timeout=5)
      status = request.status_code
      if ("API" in r.text) and (status in [200,202,203,301,302,308]):
        df.loc[df['meta.tool_homepage_url']==url,'API'] = 1
    except:
      tb.print_exc()
  df.loc[df['API'].isna(),'API'] = 0
  save_to_file(file)
  print('Assessment 5 is done')
  #-------------------------------------------------------------------------------------------------------------------------------------
  # 6) Metadata license
  # Licensing information is provided on the tool’s homepage?
  #-------------------------------------------------------------------------------------------------------------------------------------
  df = pd.read_csv(os.path.join(PTH,"data",file))
  License = ['License']
  df['license'] = 0
  for url in df['meta.tool_homepage_url']:
    try:
      r = requests.get(url,allow_redirects=True, timeout=5)
      x = [ x for x in License if x.lower() in r.text.lower()]
      if len(x) > 0:
        df.loc[df['meta.tool_homepage_url']==url,'license'] = 1
    except:
      tb.print_exc()
  save_to_file(file)
  print('Assessment 6 is done')
  #-------------------------------------------------------------------------------------------------------------------------------------
  # 7) Source code is shared in a public repository and is documented
  #-------------------------------------------------------------------------------------------------------------------------------------
  # github is available
  df = pd.read_csv(os.path.join(PTH,"data",file))
  Source_code = ['github', 'code','SourceForge']
  df['Source_code'] = 0
  for url in df['meta.tool_homepage_url']:
    if 'github' in url:
      df.loc[df['meta.tool_homepage_url']==url,'Source_code'] = 1 # github tools have a source code
    else:
      try:
        r = requests.get(url,allow_redirects=True, timeout=5)
        x = [ x for x in Source_code if x.lower() in r.text.lower()]
        if len(x) > 0:
          df.loc[df['meta.tool_homepage_url']==url,'Source_code'] = 1
      except:
        tb.print_exc()
  save_to_file(file)
  print('Assessment 7 is done')
  #-------------------------------------------------------------------------------------------------------------------------------------
  # Resource uses formal language/ FAIR vocabulary
  # Tutorials for the tool are available on the tool’s homepage
  #-------------------------------------------------------------------------------------------------------------------------------------
  # webpage contains tutorial or help
  df = pd.read_csv(os.path.join(PTH,"data",file))
  Tutorial = ['tutorial', 'help','manual']
  df['Tutorial'] = 0
  for url in df['meta.tool_homepage_url']:
    if 'github' in url:
      df.loc[df['meta.tool_homepage_url']==url,'Tutorial'] = 1
    else:
      try:
        r = requests.get(url,allow_redirects=True, timeout=5)
        x = [ x for x in Tutorial if x.lower() in r.text.lower()]
        if len(x) > 0:
          df.loc[df['meta.tool_homepage_url']==url,'Tutorial'] = 1
      except:
        tb.print_exc()
  save_to_file(file)
  print('Assessment 8 is done')
  #-------------------------------------------------------------------------------------------------------------------------------------
  # 9) Contact information is provided for the creator(s) of the tool and information describing how to cite the tool is provided
  #-------------------------------------------------------------------------------------------------------------------------------------
  # webpage contains any of the words 'about', 'email', 'contact','References','Affiliations'
  df = pd.read_csv(os.path.join(PTH,"data",file))
  Contact = ['about', 'email', 'contact','References','Affiliations']
  df['Contact'] = 0
  for url in df['meta.tool_homepage_url']:
    print(url)
    if 'github' in url:
      df.loc[df['meta.tool_homepage_url']==url,'Contact'] = 1
    else:
      try:
        r = requests.get(url,allow_redirects=True, timeout=5)
        x = [ x for x in Contact if x.lower() in r.text.lower()]
        if len(x) > 0:
          df.loc[df['meta.tool_homepage_url']==url,'Contact'] = 1
      except:
        tb.print_exc()
  save_to_file(file)
  # rename columns
  df.rename(columns={ 'license': 'Licensing information is provided on the tools home page', 
                      'unique_name': 'The tool has a unique name and an informative description',
                      'tool_url_is_active': 'The tool can be freely downloaded or accessed from a webpage',
                      'Machine_readable_metadata': 'Machine readable metadata',
                      'Totorial': 'Tutorials for the tool are available on the tool’s homepage',
                      'Source_code': 'Source code is shared in a public repository and is documented',
                      'Contact': 'Contact information is provided for the creator(s) of the tool and information describing how to cite the tool is provided',
                      'API': 'The tool can be accessed programmatically through an API and follows community standards for open APIs',
                      'Does_the_tool_contains_DOI': 'A standardized ID or accession number is used to identify the dataset'
                      }, inplace=True)
  save_to_file(file)
  print('Assessment 9 is done')

#-------------------------------------------------------------------------------------------------------------------------------------
# Upload tool assesment to Fairshake
#-------------------------------------------------------------------------------------------------------------------------------------
def upload_to_fairshake(tool_df):
  # ---------------------------------------------------------------------------------------------------------
  # A Rubric contains many Matrics
  # A Matric is an assessment method to evaluate many Tools (objects)
  
  # create matrics
  matrics_dic = {
              'description': [
                'A core aspect of data reusability is the ability to determine, unambiguously and with relative ease, the conditions under which you are allowed to reuse the (meta)data.  Thus, FAIR data providers must make these terms openly available.  This applies both to data (e.g. for the purpose of third-party integration with other data) and for metadata (e.g. for the purpose of third-party indexing or other administrative metrics)',
                "Most people use a search engine to initiate a search for a particular digital resource of interest. If the resource or its metadata are not indexed by web search engines, then this would substantially diminish an individual's ability to find and reuse it. Thus, the ability to discover the resource should be tested using i) its identifier, ii) other text-based metadata.", 
                'The change to an identifier scheme will have widespread implications for resource lookup, linking, and data sharing. Providers of digital resources must ensure that they have a policy to manage changes in their identifier scheme, with a specific emphasis on maintaining/redirecting previously generated identifiers.', 
                'Metadata play an important role in enable users to find a resource of interest. Metadata may be indexed to facilitate keyword searches over structured and unstructured metadata. However, only with structured metadata can an indexing system provide increased precision of combining keyword searches with restrictions on particular attributes e.g. license or standards used.', 
                'Some digital resources comprise of sensitive data, and require additional measures (such as institutional review board approval) to be followed before access can be granted. The ‘A’ in FAIR does not imply that the resource must be ‘Open’ or ‘Free’, but it does require that the exact conditions and the process to access restricted data are transparent and made public. Any additional authentication and authorization procedures must be specified. Therefore, prior to the release of a restricted digital resource, publishers must take steps to clarify eligibility and process. To satisfy this metric, the resource is either provided with no additional security protocol, or that the protcol is clearly specified in a web-accessible document (preferably the resource metadata!)', 
                'Digital resources and their metadata should be retrievable throguh standardised communication protocols. Open, free, and standardised communication protocols reduce the cost and effort for any part to gain authorized access to a digital resource. Having a protocol that is open allows any individual to create their own standard-compliant implementation, that it is free reduces the possibility that those lacking monetary means cannot access the resource, and that it is universally implementable ensures that such technology is available to all (and not restricted, for instance by country or creed). The resource should be accessble through an open, free, and standardized communication protocol such as TCP/IP (as opposed to a closed protocol such as the Skype telephony protocol)', 
                "Reusability is not only a technical issue; data can be discovered, retrieved, and even be machine-readable, but still not be reusable in any rational way. Reusability goes beyond 'can I reuse this data?” to other important questions such as “may I reuse this data?', 'should I reuse this data', and 'who should I credit if I decide to use it?'.", 
                'The availability of machine-readable metadata that describes a digital resource.', 
                'The tool or the paper describing it contains a unique identifier. It is a necessary condition to unambiguously refer to a resource. An identifier shared by multiple resources will confound efforts to describe that resource, or to use the identifier to retrieve it.'
                ],
              'title': [
                'Licensing information is provided on the tools home page', 
                'The tool has a unique name and an informative description',
                'The tool can be freely downloaded or accessed from a webpage',
                'Machine readable metadata',
                'Tutorials for the tool are available on the tool’s homepage',
                'Source code is shared in a public repository and is documented',
                'Contact information is provided for the creator(s) of the tool and information describing how to cite the tool is provided',
                'The tool can be accessed programmatically through an API and follows community standards for open APIs',
                'A standardized ID or accession number is used to identify the dataset'
                ],
              'rationale': [
                'https://purl.org/fair-metrics/FM_R1.1',
                'https://purl.org/fair-metrics/FM_F4',
                'https://purl.org/fair-metrics/FM_F1B',
                'https://purl.org/fair-metrics/FM_F2',
                'https://purl.org/fair-metrics/FM_A1.2',
                'https://purl.org/fair-metrics/FM_A1.1',
                'https://purl.org/fair-metrics/FM_R1.2',
                'https://purl.org/fair-metrics/FM_F2',
                'https://purl.org/fair-metrics/FM_F1A'
              ],
              'principle': ['R','F','F','F' , 'A' , 'A', 'R', 'F', 'F']
            }
  
  matrics_df = pd.DataFrame(matrics_dic)
  matrics_df['matric_id'] = ''
  
  for i in range(len(matrics_df)):
    metric = client.action(schema, ['metric', 'create'], params=dict(
    title= matrics_df.iloc[i]['title'],
    description=matrics_df.iloc[i]['description'],
    type='url',
    tags='btools',
    license='Free',
    rationale=matrics_df.iloc[i]['rationale'],
    principle=matrics_df.iloc[i]['principle'],
    ))
    matrics_df['matric_id'][i] = metric['id']
  
  # Create a rubric
  rubric = client.action(schema, ['rubric', 'create'], params=dict(
    title='ToolStory Assessments',
    description='Evaluation of tools and datasets.',
    tags='Tools, CF, NIH',
    type='tool',
    license='Free',
    metrics= matrics_df['matric_id'].tolist(),
  ))
  rubric_id = rubric['id']
  
  # load tools
  df['obj_id'] = ''
  df=df.fillna(0)
  # Create a digital objects (i.e., tools)
  for i in range(1507,len(df)):
    print(i)
    obj = client.action(schema, ['digital_object', 'create'], params=dict(
      url= df.iloc[i]['meta.tool_homepage_url'],
      title = df.iloc[i]['meta.Tool_Name'],
      description = df.iloc[i]['meta.Tool_Description'],
      type = 'tool',
      projects = [],
      rubrics = [rubric_id],
    ))
    df['obj_id'][i] = obj['id']
  
  # Create a project
  proj = client.action(schema, ['project', 'create'], params=dict(
    url='http://my-objects.com',
    title='btools',
    description='btools evaluation project',
    tags='btools',
    digital_objects=df['obj_id'].tolist(),
  ))
  proj_id = proj['id']
  
  # Create tools assessment
  assessments_df = tool_df.iloc[:,81:]
  assessments_df = assessments_df[matrics_df['title']]
  assessments_df['obj_id'] = tool_df['obj_id']
  
  for i in range(len(assessments_df)):
    print(i)
    client.action(schema, ['assessment', 'create'], params=dict(
      project=proj_id,
      target=int(assessments_df.iloc[i]['obj_id']),
      rubric=rubric_id,
      methodology='auto',
      answers=[ {"metric":int(metric), "answer":int(answer)} for metric, answer in zip(matrics_df['matric_id'].tolist(), assessments_df.iloc[i,0:len(assessments_df.columns)-1].tolist())]
      ,
    ))

#----------------------------------------------- MAIN ------------------------------------------------------
if __name__=="__main__":
  # load CF_tools
  onlyfiles = [f for f in listdir(os.path.join(PTH,'data')) if isfile(join(os.path.join(PTH,'data'), f))]
  for file in onlyfiles:
    if 'classified_tools_' in file:
      print('processing',file)
      df = pd.read_excel(os.path.join(PTH,"data/",file))
      print('Starting Fair assessment for:',file)
      FAIRshakeit(df,file)
      print('Uploading assessments for:',file)
      upload_to_fairshake(df)
      print("Done uploading assessments")
      
      
      
# delete a project from FAIRshake
# detete a project
curl -H 'Content-Type: application/json' -H 'Authorization: Token yourtokenlettershere' -X DELETE https://fairshake.cloud/project/109/






