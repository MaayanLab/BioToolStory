#################################################################
#################################################################
#################################################################
#################################################################
##### Author: Denis Torre
##### Modified by: Megan Wojciechowicz 
##### Affiliation: Ma'ayan Laboratory,
##### Icahn School of Medicine at Mount Sinai

#############################################
########## 1. Load libraries
#############################################
##### 1. Python modules #####
from ruffus import *
import pandas as pd
import nltk, re, sklearn, json, urllib, requests, time
import urllib.request as urllib2
from sklearn.feature_extraction.text import TfidfVectorizer
from sqlalchemy import Table, MetaData
from datetime import datetime
import xml.etree.ElementTree as ET
import numpy as np
import time
from iso3166 import countries as ISO
import gensim
from gensim import corpora
##### 2. Custom modules #####
my_email=''
my_tool_name=''
api_key = ''
#############################################
########## 2. General Setup
#############################################
##### 1. Variables #####
# Define stopwords
stopwords=nltk.corpus.stopwords.words("english")
stopwords.extend(['www','mail','edu','athttps', 'doi'])

#############################################
########## 3. Get PubMed Ids
#############################################

def getPMID(doi):
    pmid = np.nan
    # pubmed_data = ET.fromstring(urllib2.urlopen('https://www.ncbi.nlm.nih.gov/pmc/utils/idconv/v1.0/?tool=my_tool&email=my_email@example.com&ids='+doi.replace('https://doi.org/', '')).read())
    # pmid = pubmed_data.find('record')
    # pmid = pmid.get('pmid')
    # if pmid is None:
    #     pmid = np.nan
    # else:
    #     pmid = int(pmid)
    time.sleep(1)
    PMID = np.nan
    pubmed_data = ET.fromstring(urllib2.urlopen('https://www.ncbi.nlm.nih.gov/pmc/utils/idconv/v1.0/?tool=my_tool&email=my_email@example.com&ids='+doi.replace('https://doi.org/', '')).read())
    pmid = pubmed_data.find('record')
    pmid = pmid.get('pmid')
    if pmid is None: # some dois are not linked to their PMID using the above API, if this is the case...instead search pubmed using the doi as the search term and extract the PMID
        time.sleep(1)
        pubmed_data = ET.fromstring(urllib2.urlopen('https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi?db=pubmed&term='+doi.replace('https://doi.org/', '')+'&retmode=xml').read())
        pmid = pubmed_data.find('.//IdList')
        pmid = pmid.find('Id').text
        PMID = int(pmid)
    else:
        PMID = int(pmid)

    print(PMID)
    return(PMID)


#############################################
########## 3. Check Availability 
#############################################
def url_availability(URLS):
    count = 0
    status = []
    redirect = []
    for url in URLS:
        count = count + 1
        try:
            r = requests.get(url,timeout=30)
            if r.history:
                redirect.append(1)
            else:
                redirect.append(0)
            status.append(str(r.status_code))
            print(count)
            print(r.status_code)
        except requests.exceptions.RequestException as e:
            print(e)
            status.append(e)
            redirect.append(0)
            
    return(status,redirect)

#############################################
########## 4. Metrics API
#############################################
def metrics_from_doi(doi):
    # Altmetric API URL
    altmetric_url = 'https://api.altmetric.com/v1/doi/'+doi.replace('https://doi.org/', '')

    metrics_data = {}

    # Read URL
    try:

        # Read results
        altmetric_data = json.loads(urllib2.urlopen(altmetric_url).read())
        
        # try to get number of tweets if the data exists
        cited_by_tweeters_count = np.nan
        try:
            cited_by_tweeters_count=altmetric_data['cited_by_tweeters_count']
        except:
            pass
        # Get data
        metrics_data = {
            'doi': doi,
            'attention_score': altmetric_data['score'],
            'altmetric_badge': altmetric_data['images'].get('small'),
            'readers_count':altmetric_data['readers_count'],
            'attention_percentile': altmetric_data['context']['similar_age_3m']['pct'],
            'cited_by_tweeters_count': cited_by_tweeters_count  
        }
    except:

        # Return empty dict
        metrics_data = {'doi': doi, 'attention_score': None, 'altmetric_badge':None,'readers_count':None, 'attention_percentile': None, 'cited_by_tweeters_count':None}

    # Return
    print(json.dumps(metrics_data))
    return(json.dumps(metrics_data))

#############################################
########## 4. PubMed API - Affiliations 
#############################################

def get_author_info(pmid):
    
    time.sleep(0.2)
    affiliations = []
    try:
        pubmed_data = ET.fromstring(urllib2.urlopen('https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi?db=pubmed&id='+str(pmid)+'&retmode=xml&tool='+my_tool_name+'&email='+my_email+'&api_key='+api_key).read())
        for author in pubmed_data.findall('.//Author'):            
            affiliation = "None"    
            try:
                affiliation = author.find('.//Affiliation').text            
            except:
                pass       
            affiliations.append(affiliation)
    except:
        affiliations.append("None")   
    print(affiliations)   
    return(affiliations)

#############################################
######### 4. # Get Pubmed citations #########
#############################################

def get_pubmed_citations(pmid):

    citations = np.nan
    time.sleep(0.2)
    try:
        # PubMed API URL
        pubmed_data = ET.fromstring(urllib2.urlopen('https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esummary.fcgi?db=pubmed&tool='+my_tool_name+'&email='+my_email+'&api_key='+api_key+'&id='+str(pmid)).read())         
        citations = int(pubmed_data.find('DocSum/Item[@Name="PmcRefCount"]').text)
    except:
        pass
    print(citations)   
    return(citations)
    
#############################################
########### 4. Get PMIDs that ###############
########## reference each tool ##############
########## and the coresponding #############
########## years they were published ########
#############################################
def get_references(pmid):
    time.sleep(0.5)
    references = []
    try:
        pubmed_data = ET.fromstring(urllib2.urlopen('https://eutils.ncbi.nlm.nih.gov/entrez/eutils/elink.fcgi?dbfrom=pubmed&linkname=pubmed_pubmed_citedin&id='+str(pmid)+'&tool='+my_tool_name+'&email='+my_email+'&api_key='+api_key).read())       
        for link in pubmed_data.findall('.//LinkSetDb'):            
           for Id in link.findall('.//Id'):               
               references.append(Id.text)
    except: 
        pass
    print('references:'+str(len(references))) 
    return(references)

def get_reference_year(pmids):
    time.sleep(0.5)
    years =   []
    try:
        pubmed_data = ET.fromstring(urllib2.urlopen('https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi?db=pubmed&id='+str(pmids)+'&retmode=xml&tool='+my_tool_name+'&email='+my_email+'&api_key='+api_key).read())   
        for date in pubmed_data.findall('.//PubDate'):
            try:
                year = date.find('Year').text
                years.append(year)
            except:
                year = date.find('MedlineDate').text.split(' ')[0] 
                years.append(year)


        # for article in pubmed_data.findall('.//PubmedArticle'):
        #     try:
        #         date = article.find('.//PubDate')
        #         years.append(date.find('Year').text)
        #     except:
        #         years.append(article.find('MedlineDate').text.split(' ')[0])    
    except:
        pass    
    return(years)




def get_country(affiliations):
   
    aff = [str(x).replace('[','').replace(']','').replace("'",'') for x in affiliations]

    # get last author affiliation if possible, otherwiese get first author 
    aff = [x.split(';')for x in aff]
    aff = [x[-1] if x[-1] != 'None' else x[0] for x in aff]
    aff = [x.strip('.') for x in aff]
  

    aff_split = [x.split(', ') for x in aff]

    
    # get countries (usually at the end the affiliation)
    countries = []
    for x in aff_split:
        if len(x[-1].split(' '))==1 and '@' in x[-1] and len(x) >1:
                countries.append(x[-2])         
        else:
            if len(x[-1].split(' '))==1 and len(re.findall('[0-9]', x[-1]))>0 and len(x) >1:
                countries.append(x[-2])
            else:
                total = 0
                segs = x[-1].split(' ')
                for seg in segs:
                    if len(re.findall('[0-9]', seg))>0:
                        total = total+1
                    else:
                        if '@' in seg:
                            total = total+1
                if len(segs) <= total & len(x) >1:
                    countries.append(x[-2])
                else:
                    countries.append(x[-1])
                


    # remove emails, make lowercase
    def remove_emails(affiliations):
        countries_fixed = []
        for country in affiliations:
            segs = country.split(' ')
            remove = []
            if len(segs)>1:
                for seg in segs:  
                    if '@' in seg: # remove all emails
                        remove.append(seg)    
                    if '-or-' in seg: # remove all emails
                        remove.append(seg)    
            else:
                segs = [x.strip('.') for x in segs]
            final = ' '.join([x.strip('.') for x in segs if x not in remove])
            final = final.replace(u'\xa0',' ')
            final = final.replace('-',' ')
            final = final.lower()
            final = final.replace('contact','')
            final = final.replace(':','')
            countries_fixed.append(final)   
        return(countries_fixed)
    
    countries =  remove_emails(countries)  
 

    def remove_zipcodes(affiliations):
        countries_fixed = []
        for country in affiliations:
            finish = ''
            country_segs = []
            segs = country.split(' ')
            if len(segs)>1:
                for i,seg in reversed(list(enumerate(segs))):           
                    if len(re.findall('[0-9]', seg))==0:
                        finish = 'stop'
                        country_segs.append(seg)   
                    else:
                        if finish=='stop':
                            break
            else:
                country_segs = [x.replace('.','') for x in segs]
            countries_fixed.append(' '.join([x.replace('.','') for x in reversed(list(country_segs))]))   
        return(countries_fixed)        

    countries =  remove_zipcodes(countries)   
                 
    countries = [re.sub(r'\sand$', '', x,flags=re.I).strip() for x in countries] # remove the word 'and' at the end of a string

    return (aff, countries)



def get_institution(affiliations):

    # aff = [str(x).replace('[','').replace(']','').replace("'",'') for x in affiliations]

    # # get last author affiliation if possible, otherwiese get first author 
    # aff = [x.split(';')for x in aff]
    # aff = [x[-1] if x[-1] != 'None' else x[0] for x in aff]
    # aff = [x.strip('.') for x in aff]
    #aff = [x.split(', ') for x in affiliations]
    aff = [re.split(r',\s*(?![^()]*\))',x) for x in affiliations]
    institutions = []

    # for a in aff:
    #     institution = ''
    #     for name in ['universi','school','college','instit','center','centr','academy','lab']:
    #         for x in a:
    #             if name in x.lower():
    #                 institution = x
    #                 break
    #         if institution != '':
    #             break
    #     if institution == '':
    #         try:
    #             institution = a[1]
    #         except:
    #             institution = a[0]
    #     institutions.append(institution)
    for a in aff:
        final = []
        for name in ['universi','school','college','instit','center','centr','academy','lab']:
             for x in a :
                 x = x.replace(',','')
                 if name in x.lower():
                     if x not in final:
                        final.append(x)
        if len(final)==0:
            final.append(a[0])
        final = np.unique(final)
        institutions.append(str(','.join(final)))
   
    return(institutions)


#############################################
########## 5. Process Text
#############################################

# Process text
def process_text(text,stem):
    
    # Compile regular expression
    remove_characters = re.compile(b'[^a-zA-Z ]+')
   
    # Remove special characters and make lowercase
    processed_text=re.sub(remove_characters, b'', text.encode('ascii', 'ignore').strip().lower())
    processed_text=processed_text.decode('ascii')
    
    # Tokenize
    processed_text = [x.strip() for x in nltk.word_tokenize(processed_text)]

    # Remove stopwords
    processed_text = [x for x in processed_text if x not in stopwords]

    # Check length
    processed_text = [x for x in processed_text if len(x) < 20 and 'http' not in x]
   
    # Stem
    if stem == 'stem':
        processed_text = [nltk.PorterStemmer().stem(x) for x in processed_text]

    # Tag and make lowercase
    #processed_text = [(word.lower(), penn_to_wn_tags(pos_tag)) for word, pos_tag in tag(" ".join(processed_text))]        
    
    # Check if exists
    #processed_text = [x for x in processed_text if nltk.corpus.wordnet.synsets(x)]
    
    # Join
    processed_text = " ".join(processed_text)
    
    # Return
    return processed_text

#############################################
########## 6. Similarity and keywords
#############################################

# Get similarity and keywords
def extract_text_similarity_and_keywords(processed_texts, labels, n_keywords=5, identifier='doi'):

    # Get vectorized
    tfidf_vectorizer = TfidfVectorizer(min_df=0.00,max_df=0.1, strip_accents='unicode', ngram_range=(1, 1)) # added strip accents

    # Get matrix
    tfidf_matrix = tfidf_vectorizer.fit_transform(processed_texts).astype(float)

    #Calculate the adjacency matrix
    similarity_dataframe = pd.DataFrame(sklearn.metrics.pairwise.cosine_similarity(tfidf_matrix, tfidf_matrix), index=labels, columns=labels)

    # Feature dataframe
    feature_dataframe = pd.DataFrame(tfidf_matrix.todense(), index=labels, columns=tfidf_vectorizer.get_feature_names())
    
    # Melt
    #feature_dataframe_melted = pd.melt(feature_dataframe.reset_index(drop=True).rename(columns={'level_0': identifier}), id_vars=identifier, var_name='keyword', value_name='importance') # need if stemming text
    feature_dataframe_melted = pd.melt(feature_dataframe.reset_index().rename(columns={'level_0': identifier}), id_vars=identifier, var_name='keyword', value_name='importance')

    # Get keywords dataframe .loc[[nltk.corpus.wordnet.synsets(x) for x in feature_dataframe_melted['keyword']]]
    keyword_dataframe = feature_dataframe_melted.dropna().groupby(identifier)['keyword','importance'].apply(lambda x: x.nlargest(n_keywords, columns=['importance'])).reset_index().set_index(identifier).drop_duplicates().drop(['level_1', 'importance'], axis=1)

    # Return
    return similarity_dataframe, keyword_dataframe








