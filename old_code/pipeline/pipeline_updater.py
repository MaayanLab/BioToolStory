#################################################################
#################################################################
############### Canned Analyses ################
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
import sys, os, glob, json, re 
import pandas as pd
import numpy as np
import gensim 
from gensim.utils import simple_preprocess
from gensim.parsing.preprocessing import STOPWORDS
from nltk.stem import WordNetLemmatizer, SnowballStemmer
from nltk.stem.porter import *
from nltk.stem import *
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.feature_extraction.text import CountVectorizer
from sqlalchemy import create_engine, and_, or_
from sqlalchemy.orm import sessionmaker
from sqlalchemy import Table, MetaData
import datetime
import time 
from collections import Counter
import itertools
#import lda
from sklearn.decomposition import LatentDirichletAllocation
from sklearn.model_selection import GridSearchCV
import matplotlib.pyplot as plt
import country_mapping as country_mapper
import nltk
import seaborn as sns
from sklearn.manifold import TSNE
nltk.download('wordnet')

# R connection
from rpy2.robjects import r, pandas2ri
pandas2ri.activate()

##### 2. Custom modules #####
# Pipeline running
sys.path.append('article_scraper')
import Pipeline_Updater_Support as P

# #############################################
# ########## 2. General Setup
# #############################################
# ##### 1. Variables #####

# Spiders
spiders = ['oxford','bmc_bioinformatics']

# Remove results scraped from BMC Bioinformatics before a defined year (2008)
year_threshold = time.strptime('2008-01-01', '%Y-%m-%d')

##### 2. R Connection #####
r.source('pipeline/pipeline_updater.R')

#############################################
########## 1. Run Spiders
#############################################
@follows(mkdir('s1-spider_results.dir'))

def spiderJobs():
	for spider in spiders:
		yield [None,spider]

@files(spiderJobs)

def runSpiders(infile, outfile):
	
	# Change directory
	os.chdir('article_scraper')
	
	# Run
	os.system('scrapy crawl '+outfile)

	# Move back
	os.chdir('..')

#############################################
##### 2. Extract Tools
#############################################

# @follows(runSpiders)
@follows(mkdir('s2-tools.dir'))

@transform(glob.glob('s1-spider_results.dir/*/*.json'),
		  regex(r"s1-spider_results.dir/.*/(.*).json"),
		  r"s2-tools.dir/\1_tools.txt")

def getTools(infile, outfile):

	# Print
	print('Doing {}...'.format(outfile))
	
	# Initialize dataframe
	tool_dataframe = pd.DataFrame()

	# Get dataframe
	with open(infile) as openfile:

		# Get dataframe
		tool_dataframe = pd.DataFrame(json.loads(openfile.read())['article_data'])[['article_title', 'links', 'doi', 'date']]

		# Drop no links
		
		tool_dataframe.drop([index for index, rowData in tool_dataframe.iterrows() if len(rowData['links']) == 0], inplace=True)

		# Add link column
		tool_dataframe['tool_homepage_url'] = [x[0] for x in tool_dataframe['links']]

		# Drop links columns
		tool_dataframe.drop('links', inplace=True, axis=1)
		
		# Add tool name column
		tool_dataframe['tool_name'] = [x.split(':')[0].replace('"', '') if ':' in x and len(x.split(':')[0]) < 50 else None for x in tool_dataframe['article_title']]

		# Drop rows with no names
		tool_dataframe.drop([index for index, rowData in tool_dataframe.iterrows() if not rowData['tool_name']], inplace=True)

		# Add tool description
		tool_dataframe['tool_description'] = [x.split(':', 1)[-1].strip() for x in tool_dataframe['article_title']]
		tool_dataframe['tool_description'] = [x[0].upper()+x[1:] for x in tool_dataframe['tool_description']]
		
		# Drop article title
		tool_dataframe.drop('article_title', inplace=True, axis=1)
		
	# Check if tool link works
	indices_to_drop = []

	# Loop through indicies
	for index, rowData in tool_dataframe.iterrows():

		# Try to connect
		try:
			# Check URL
			if 'http' in rowData['tool_homepage_url']: #urllib2.urlopen(rowData['tool_homepage_url']).getcode() in (200, 401)
				pass
			else:
				# Append
				indices_to_drop.append(index)
		except:
				# Append
				indices_to_drop.append(index)

	# Drop
	tool_dataframe.drop(indices_to_drop, inplace=True)

	# Write
	tool_dataframe.to_csv(outfile, sep='\t', index=False, encoding='utf-8')

#############################################
########## 3. Extract Articles
#############################################

@follows(mkdir('s3-articles.dir'))
@follows(getTools)

@transform(glob.glob('s1-spider_results.dir/*/*.json'),
		  regex(r"s1-spider_results.dir/.*/(.*).json"),
		  add_inputs(r"s2-tools.dir/\1_tools.txt"),
		  r"s3-articles.dir/\1_articles.txt")

def getArticles(infiles, outfile):

	# Print
	print('Doing {}...'.format(outfile))

	# Split infiles
	jsonFile, toolFile = infiles

	# Get dataframe
	with open(jsonFile, 'r') as openfile:

		# Get dataframe
		article_dataframe = pd.DataFrame(json.loads(openfile.read())['article_data']).drop('links', axis=1)
		
		# Join authors
		article_dataframe['authors'] = ['; '.join(x) for x in article_dataframe['authors']]
		
		# Fix abstract
		article_dataframe['abstract'] = [json.dumps({'abstract': x}) for x in article_dataframe['abstract']]
		
	# Get tool DOIs
	toolDois = pd.read_table(toolFile)['doi'].tolist()

	# Intersect
	article_dataframe = article_dataframe.set_index('doi').loc[toolDois].reset_index()

	# Get Journal FK dict
	journal_fks = {'bioinformatics': 1, 'database': 2, 'nar': 3, 'bmc-bioinformatics': 4}

	# Add journal fk
	article_dataframe['journal_fk'] = journal_fks[os.path.basename(outfile).split('_')[0]]

	# Write
	article_dataframe.to_csv(outfile, sep='\t', index=False, encoding='utf-8')

#############################################
########## 4. Tool Table
#############################################

@follows(mkdir('s4-tables.dir'))
@merge(getTools,
	   's4-tables.dir/tool-table.txt')

def prepareToolTable(infiles, outfile):

	# Get dataframe
	tool_dataframe = pd.concat([pd.read_table(x) for x in infiles])
	
	# Remove any tools scraped before year 2008
	tool_dataframe['date'] =  pd.to_datetime(tool_dataframe['date'], format='%d %B %Y')
	
	tool_dataframe = tool_dataframe[tool_dataframe['date'].dt.year >= year_threshold.tm_year]

	tool_dataframe = tool_dataframe.drop(['date'], axis=1)

	# Write to outfile
	tool_dataframe.to_csv(outfile, sep='\t', index=False)

#############################################
########## 5. Article Table
#############################################

@merge(getArticles,
	   's4-tables.dir/article-table.txt')

def prepareArticleTable(infiles, outfile):

	# Get dataframe
	article_dataframe = pd.concat([pd.read_table(x) for x in infiles])

	# Remove articles scraped before year 2008
	article_dataframe['date'] =  pd.to_datetime(article_dataframe['date'], format='%d %B %Y')
	
	article_dataframe = article_dataframe[article_dataframe['date'].dt.year >= year_threshold.tm_year]

	# Write to outfile
	article_dataframe.to_csv(outfile, sep='\t', index=False)

#############################################
########## 6. Merge Article/Tool Table
#############################################

@follows(prepareArticleTable)
@follows(prepareToolTable)
@merge((prepareToolTable, prepareArticleTable),	
		('s4-tables.dir/article-tool-table-merged.tsv','s4-tables.dir/article-tool-table-merged.csv'))

def mergeArticleToolTable(infiles,outfile):
	
	tool_table, article_table = infiles 
	
	tool_table = pd.DataFrame(pd.read_table(tool_table))	

	article_table = pd.DataFrame(pd.read_table(article_table))

	df = pd.merge(tool_table, article_table, on='doi',how='left')

	# remove duplicate dois 
	df = df.drop_duplicates(subset=['doi'], keep='first')
	
	# Convert date time format 
	df['date'] =  pd.to_datetime(df['date'], format='%Y-%m-%d')

	# remove tabs and newlines from article title and abstracts
	df = df.replace('\t','')
	
	df['article_title']=[str(x).strip('\t') for x in df['article_title']] 
	
	df['article_title']=[str(x).replace('\n','') for x in df['article_title']] 
	
	df['authors']=[str(x).replace('\t','') for x in df['authors']]
	
	df['authors']=[str(x).replace('\n','') for x in df['authors']]
	
	df['tool_description']=[str(x).replace('\n','') for x in df['tool_description']]
	
	df['tool_description']=[str(x).replace('\t','') for x in df['tool_description']]

	# remove spaces from beginning and end of tool names
	df['tool_name']=[str(x).strip() for x in df['tool_name']] 

	# Calculate age of tool
	todays_date = datetime.datetime.strptime(str(datetime.date.today()),'%Y-%m-%d') 

	df['age_years'] = [((todays_date-date).days)/365 for date in df['date']]

	df['age_days'] = [((todays_date-date).days) for date in df['date']]

	# Get journal Name
	journal_fks_reverse_dict={1:'Bioinformatics',2:'Database',3:'Nucleic Acids Research',4:'BMC Bioinformatics'}
    
	df['journal_name'] = [journal_fks_reverse_dict[int(x)] for x in df['journal_fk']]

	# Get year of publish date
	df['pub_year'] = list([x.year for x in df['date']])

	# Get last author
	df['last_author'] = list([x.split(';')[-1].strip() for x in df['authors']])

	# replace characters that are inconsistent
	df['last_author'] = [str(x).replace('’','\'') for x in df['last_author']]

	# Standardize tool names
	standard_tool_names=[]
	for x in df['tool_name']:
		# filters to standardize tool names 
		x=x.replace(',','')
		x=re.sub(r'(\-\d+\.*\d*$)','',x, flags=re.I) # removes '-1.0' at end of name
		x=re.sub(r'(\s+\bversion\b.*$)','',x, flags=re.I) # removes 'version ......' at end of name
		x=re.sub(r'(\s+\bin\b\s+\d+$)', '', x, flags=re.I)   # removes 'in year' at end of name
		x=re.sub(r'(\s+v*\.*\d+\.*\d*$)', '', x, flags=re.I) # removes v, 2 , 2.0 after toolname
		x=re.sub(r'(\s+\(*\bupdate\b\)*.*$)','',x, flags=re.I) # removes 'update .....' at end of name
		x=re.sub(r'(\s+\(*\brelease\b\)*.*$)','',x, flags=re.I) # removes 'release ....' at end of name
		x=re.sub(r'(^\bupdate\b\s+\bof\b\s+\bthe\b\s+)','',x, flags=re.I) # removes 'Update of the....' at start of name
		x=re.sub(r'(V*\d+\.*\d*$)','',x, flags=re.I) # removes V3 or V3.0 atached to name
		x=re.sub(r'(\d+\.+\d+$)','',x, flags=re.I) # removes 2.0 attached to name
		x=x=re.sub(r'(\(+.*\)+)','',x, flags=re.I)# removes everything in parentheses
		standard_tool_names.append(x)
		
	df['standardized_tool_name']=standard_tool_names

	# Write to outfile
	df.to_csv(outfile[0], sep='\t', index=False)
	df.to_csv(outfile[1], sep=',', index=False)

#############################################
########## 7. Get PubMed Ids
#############################################
@follows(mkdir('s5-stats.dir'))
@follows(mergeArticleToolTable)
@merge(mergeArticleToolTable,('s5-stats.dir/pmid.tsv','s5-stats.dir/pmid.csv'))

def getPMID(infile,outfile):

	df = pd.DataFrame(pd.read_table(infile[0], sep = '\t'))

	pmids = []       

	for doi in df['doi']:

		pmids.append(P.getPMID(doi))
	
	df['pmid'] = list(pmids)

	# Write to outfile
	df.to_csv(outfile[0], sep='\t', index=False)
	df.to_csv(outfile[1], sep=',', index=False)

#############################################
########## 7. Get Altmetric scores
#############################################
@follows(getPMID)
@merge(getPMID,('s5-stats.dir/pmid_altmetrics.tsv','s5-stats.dir/pmid_altmetrics.csv'))

def getAltmetrics(infile,outfile):
	
	df = pd.DataFrame(pd.read_table(infile[0], sep = '\t'))
	
	metrics=[]
	
	for doi in df['doi']:
		
		time.sleep(0.5)

		metrics.append(json.loads(P.metrics_from_doi(doi)))
	
	metric_score_dataframe = pd.DataFrame(metrics)
	
	df=pd.merge(df, metric_score_dataframe, on='doi',how='left')

	# Write to outfile
	df.to_csv(outfile[0], sep='\t', index=False)
	df.to_csv(outfile[1], sep=',', index=False)

#############################################
########## 8. Get availability
#############################################
@follows(getAltmetrics)
@merge(getAltmetrics,('s5-stats.dir/pmid_altmetrics_availability.tsv','s5-stats.dir/pmid_altmetrics_availability.csv'))

def getAvailability(infile,outfile):
	
	df = pd.DataFrame(pd.read_table(infile[0], sep='\t'))
	
	codes, redirects = P.url_availability(df['tool_homepage_url'])

	df['tool_homepage_http_code']=codes

	df['redirect'] = redirects

	# Create a column for up(1) or down (0) urls
	up_down=[]
	ok = [x for x in range(200,300)]
	for code in df['tool_homepage_http_code']:
		try:
			if int(code) in ok:
				up_down.append(1)
			else:
				up_down.append(0)      
		except:
			up_down.append(0)
	df['up_down']=up_down

	# Write to outfile
	df.to_csv(outfile[0], sep='\t', index=False)
	df.to_csv(outfile[1], sep=',', index=False)

#############################################
########## 8. Get Author Affiliations 
#############################################
@follows(getAvailability)
@merge(getAvailability,('s5-stats.dir/pmid_altmetrics_availability_affiliations.tsv','s5-stats.dir/pmid_altmetrics_availability_affiliations.csv'))

def getAffiliations(infile,outfile):

	df = pd.DataFrame(pd.read_table(infile[0], sep='\t'))

	affiliations=[]
	
	for pmid in df['pmid']:
		
		aff = P.get_author_info(pmid)
		affiliations.append(';'.join(aff))
	
	df['author_affiliations']= affiliations

	# Write to outfile
	df.to_csv(outfile[0], sep='\t', index=False)
	df.to_csv(outfile[1], sep=',', index=False)


######################################################
######################################################
########## S3. Get total pubmed ###################### 
############### citations ############################ 
######################################################
######################################################
@follows(getAffiliations)
@merge(getAffiliations,('s5-stats.dir/pmid_altmetrics_availability_affiliations_pubcitations.tsv','s5-stats.dir/pmid_altmetrics_availability_affiliations_pubcitations.csv'))

def getPubmedCitations(infile,outfile):

	df = pd.DataFrame(pd.read_table(infile[0], sep='\t'))

	citations = [P.get_pubmed_citations(pmid) for pmid in df['pmid']]
	
	df['total_pubmed_citations'] = citations

	# Write to outfile
	df.to_csv(outfile[0], sep='\t', index=False)
	df.to_csv(outfile[1], sep=',', index=False)
	#######################################################
#######################################################
########## S3. Get PMIDs & Pub Year for ############### 
########## 	articles that cite tools    ############### 
#######################################################
#######################################################

@follows(getPubmedCitations)
@merge(getPubmedCitations,('s5-stats.dir/pmid_altmetrics_availability_affiliations_pubcitations_references.tsv','s5-stats.dir/pmid_altmetrics_availability_affiliations_pubcitations_references.csv'))

def getReferences(infile,outfile):
	
	# Get all PMIDs for articles that cite each tool
	references = []

	df = pd.DataFrame(pd.read_table(infile[0], sep='\t'))

	count = 0

	for pmid in df['pmid']:

		count = count +1
		
		print(count)

		ref = P.get_references(pmid)

		references.append(ref)

	df['referenced_by_pmids']=references

	# Write to outfile
	df.to_csv(outfile[0], sep='\t', index=False)
	df.to_csv(outfile[1], sep=',', index=False)

	
@follows(getReferences)
@merge(getReferences,('s5-stats.dir/pmid_altmetrics_availability_affiliations_pubcitations_references_refyears.tsv','s5-stats.dir/pmid_altmetrics_availability_affiliations_pubcitations_references_refyears.csv'))
	
def getReferencesYears(infile,outfile):	
	
	df = pd.DataFrame(pd.read_table(infile[0], sep='\t'))

	#references = [x.replace('[','').replace(']','').replace("'",'').split(', ') for x in df['referenced_by_pmids']]
	references = [x.replace('[','').replace(']','').replace("'",'').replace(' ','').strip() for x in df['referenced_by_pmids']]

	all_years = []

	for r in references:
		print('references: '+str(len(r.split(','))))
	
		if len(r.split(','))>200:
			years_seg=[]
			r_list = r.split(',')
			for i in range(0,len(r_list),200):
				years_seg.append(P.get_reference_year(','.join([str(x) for x in r_list[i:i+200]])))
			all_years.append(list(itertools.chain.from_iterable(years_seg)))
			print('years: '+ str(len(list(itertools.chain.from_iterable(years_seg)))))


		else:
			#years = [pmid_year[x] for x in r]
			years = P.get_reference_year(r)
			all_years.append(years)
			print('years: '+ str(len(years)))

	df['referenced_by_pub_years']=all_years

	# Write to outfile
	df.to_csv(outfile[0], sep='\t', index=False)
	df.to_csv(outfile[1], sep=',', index=False)

#######################################################
#######################################################
########## Get Country and Institution ################
#######################################################
#######################################################

@follows(getReferencesYears)
@merge(getReferencesYears,('s5-stats.dir/final.tsv','s5-stats.dir/final.csv'))
	
def getCountriesAndInstitution(infile,outfile):

	df = pd.DataFrame(pd.read_table(infile[0], sep='\t'))

	affiliation, countries = P.get_country(df['author_affiliations'])

	df['affiliation'] = affiliation

	df['country'] = countries

	institutions = P.get_institution(df['affiliation'])

	df['institution'] = institutions


	# Convert countries manually
	df['country_final']= country_mapper.convert_countries(df)
	df = df.drop(['country'], axis=1)


	# Write to outfile
	df.to_csv(outfile[0], sep='\t', index=False)
	df.to_csv(outfile[1], sep=',', index=False)



@follows(getCountriesAndInstitution)
@merge(getCountriesAndInstitution,('s5-stats.dir/FINAL_bioinformatics_tools_analysis.tsv','s5-stats.dir/FINAL_bioinformatics_tools_analysis.csv'))
def finalProcessing (infile,outfile):

	# fix availability info for tool URLS with ',' 
	df = pd.DataFrame(pd.read_table(infile[0], sep='\t'))

	
	
	for i,url in enumerate(df['tool_homepage_url']):
		if ',' in url:
			print('url fixed:')
			print(df.iloc[i])
			url = url.strip(',')
			df['tool_homepage_url'].iloc[i] = url

			codes, redirects = P.url_availability([url])

			df['tool_homepage_http_code'].iloc[i]= codes[0]

			df['redirect'].iloc[i] = redirects[0]

			ok = [x for x in range(200,300)]
			
			try:
				if int(codes[0]) in ok:
					df['up_down'].iloc[i] = 1
				else:
					df['up_down'].iloc[i] = 0
			except:
				df['up_down'].iloc[i] = 0
	
	df['base_url'] = [x.split('://')[1] for x in df['tool_homepage_url']]
	df['base_url'] = [x if x.endswith('/')==True else str(x+'/') for x in df['base_url'] ]
	# Get URLs that occur multiple times - Standardized tool names further
	tool_names_same = Counter(df['base_url'])
	duplicate_urls = [k for k,v in tool_names_same.items() if v > 1]

	# If tools names are different for the same URL, take the most recent tool name 
	url_to_standardized_name = {}
	for url in duplicate_urls:
		df_duplicates = df[df['base_url']==url]
		names = df_duplicates['standardized_tool_name']
		if len(np.unique(names)) > 1: 
			final_name = list(df_duplicates[df_duplicates['date']==df_duplicates['date'].max()]['standardized_tool_name'])[0]
			url_to_standardized_name[url]=final_name
	
	final_names = []
	for i,url in enumerate(df['base_url']):
		try:
			final_names.append(url_to_standardized_name[url])
		except:
			final_names.append(df['standardized_tool_name'].iloc[i])
	
	# Update tool names 
	df = df.drop(['standardized_tool_name'],axis = 1)
	df['standardized_tool_name'] = final_names

	# Remove all tools published in 2019
	df = df[df['pub_year']<2019]

	# Resolve ambiguous University of California's in institutions using affiliation
	all_institutions_new = []
	for i, institiutions in enumerate(df['institution']):
			inst_new = []
			institiutions = str(institiutions).strip()
			institiutions = institiutions.split(',')
			for x in institiutions:
				# remove dashes 
				x = x.replace('-', ' ')
				# remove anything within parenthesis 
				x =  re.sub(r'\s*\(.*\)','', x)
				x = x.strip()
				x = x.replace('(','').replace(')','')
				# remove 'and' at the beginning 
				x = re.sub(r'^and\s','',x)
				
				if x == 'University of California':
						aff = df['affiliation'].iloc[i]
						aff = aff.split(',')
						aff = [a.strip() for a in aff]
						idx_UC = aff.index('University of California')
						location = re.sub(r'\s*\(.*\)','', aff[idx_UC+1]).strip()
						x = str(x + ' ' + location)
						inst_new.append(x)
				else:
					inst_new.append(x)
			all_institutions_new.append(inst_new)

	# Update institution
	df = df.drop(['institution'],axis = 1)
	df['institution'] = [','.join(inst) for inst in all_institutions_new]

	# Write to outfile
	df.to_csv(outfile[0], sep='\t', index=False)
	df.to_csv(outfile[1], sep=',', index=False)

#######################################################
#######################################################
########## S3. Tool Similarity Network
#######################################################
#######################################################


#############################################
########## 1. Get Tool Similarity
#############################################

@follows(mkdir('s6-tool_similarity.dir'))
@merge((mergeArticleToolTable),
		's6-tool_similarity.dir/related_tools.txt')

def getRelatedTools(infiles, outfile):

	# Split infiles
	#toolFile, articleFile = infiles

	# Initialize dataframe
	abstract_dataframe = pd.read_table(infiles[0])

	# Fix abstract
	# abstract_dataframe['abstract'] = [' '.join([abstract_tuple[1] for abstract_tuple in json.loads(x)['abstract'] if abstract_tuple[0] and abstract_tuple[0].lower() not in [u'contact:', u'availability and implementation', u'supplementary information']]) for x in abstract_dataframe['abstract']]
	
	# Fix abstracts-need to account for abstracts that are tuples with titles and those that are not   
	# all_abstracts = []
    
	# for x in abstract_dataframe['abstract']:
		
	# 	abstract = ' '.join([abstract_tuple[1] for abstract_tuple in json.loads(x)['abstract'] if abstract_tuple[0] and abstract_tuple[0].lower() not in [u'contact:', u'availability and implementation', u'supplementary information']])
        
	# 	if len(abstract)==1:
        	
	# 		abstract = json.loads(x)['abstract'][0]
        
	# 	all_abstracts.append(abstract)
    
	# abstract_dataframe['abstract']=all_abstracts

	all_abstracts = []

	for i,x in enumerate(abstract_dataframe['abstract']):
		
		if int(abstract_dataframe['journal_fk'].iloc[i])==2 or int(abstract_dataframe['journal_fk'].iloc[i])==3: # database and nar abstracts were scraped without titles
			
			all_abstracts.append(str(json.loads(x)['abstract'][0]))
    		
		else:

			abstract=' '.join([abstract_tuple[1] for abstract_tuple in json.loads(x)['abstract'] if abstract_tuple[0] and abstract_tuple[0].lower() not in [u'contact:', u'availability and implementation', u'supplementary information']])
		
			all_abstracts.append(abstract)

	abstract_dataframe['abstract']=all_abstracts
	
	# Process abstracts
	processed_abstracts = [P.process_text(x,'') for x in abstract_dataframe['abstract']]

	# Get similarity and keywords
	article_similarity_dataframe, article_keyword_dataframe = P.extract_text_similarity_and_keywords(processed_abstracts, labels=abstract_dataframe['doi'])

	# Get tool-doi correspondence
	#tool_dois = pd.read_table(toolFile).set_index('doi')['tool_name'].to_dict()
	tool_dois = abstract_dataframe.set_index('doi')['tool_name'].to_dict()

	# Rename similarity
	#tool_similarity_dataframe = article_similarity_dataframe.loc[tool_dois.keys(), tool_dois.keys()].rename(index=tool_dois, columns=tool_dois)
	tool_similarity_dataframe = article_similarity_dataframe.loc[tool_dois.keys(), tool_dois.keys()]
	
	# Fill diagonal
	np.fill_diagonal(tool_similarity_dataframe.values, np.nan)
	tool_similarity_dataframe.to_csv('s6-tool_similarity.dir/tool_similarity_dataframe.csv', sep = ',')
	
	# Melt tool similarity
	melted_tool_similarity_dataframe = pd.melt(tool_similarity_dataframe.reset_index('doi').rename(columns={'doi': 'source'}), id_vars='source', var_name='target', value_name='similarity').dropna()
	
	# Remove 0
	melted_tool_similarity_dataframe = melted_tool_similarity_dataframe.loc[[x > 0 for x in melted_tool_similarity_dataframe['similarity']]]
	
	# Get related tools
	related_tool_dataframe = melted_tool_similarity_dataframe.groupby(['source'])['target','similarity'].apply(lambda x: x.nlargest(5, columns=['similarity'])).reset_index().drop('level_1', axis=1)

	# Get tool keywords
	#tool_keyword_dataframe = pd.DataFrame([{'tool_name': tool_dois.get(doi), 'keyword': keyword} for doi, keyword in article_keyword_dataframe.reset_index()[['doi', 'keyword']].as_matrix() ]).dropna()
	tool_keyword_dataframe = pd.DataFrame([{'tool_name': doi, 'keyword': keyword} for doi, keyword in article_keyword_dataframe.reset_index()[['doi', 'keyword']].as_matrix() ]).dropna()
	
	# Write
	related_tool_dataframe.to_csv(outfile, sep='\t', index=False)
	tool_keyword_dataframe.to_csv(outfile.replace('.txt', '_keywords.txt'), sep='\t', index=False)


#############################################
########## 2. Filter Tool Similarity
#############################################
# Filter the similarity networks according to Avi's suggestions

def filterJobs():
	# Create separate similarity networks - separate files with 1-5 similar tools 
	for network_num in list(list(range(1,6))+list([10000])):
		for max_edges in [3,5,10,15,20,10000]:
			for remove_hub in [25,50,100,200,300,400,500,600]:
				infile = 's6-tool_similarity.dir/related_tools.txt'
				outfile = 's6-tool_similarity.dir/related_tools_filtered_top{network_num}edges_hubsmin{max_edges}edgesbroken_top{remove_hub}hubsremoved.txt'.format(**locals())
				yield (infile, outfile, network_num, max_edges, remove_hub)

@follows(getRelatedTools)
@files(filterJobs)
def filterToolSimilarity(infile, outfile, network_num, max_edges, remove_hub):

	# Print
	print('Doing {}...'.format(outfile))

	# Read related tool dataframe
	related_tool_dataframe = pd.read_table(infile).sort_values(['source', 'similarity'], ascending=False)

	# Initialize I
	occurrence = 1

	# Set source tool name
	previous_source_tool_name = None

	# Get top n similar tools
	for index, rowData in related_tool_dataframe.iterrows():
		
		# Set occurrence
		if rowData['source'] == previous_source_tool_name:
			occurrence += 1
		else: 
			occurrence = 1
				
		# Set previous tool name
		previous_source_tool_name = rowData['source']
		
		# Remove extra edges
		if occurrence > network_num:
			related_tool_dataframe.drop(index, inplace=True)

	# Remove duplicate edges 
	related_tool_dataframe = related_tool_dataframe[~related_tool_dataframe[['source', 'target']].apply(sorted, axis=1).duplicated(keep='first')]

	# Remove top num hubs  
	node_occurrences = Counter(list(related_tool_dataframe['source'])+list(related_tool_dataframe['target']))

	top_hubs = sorted(list(node_occurrences.values()),reverse=True)[0:remove_hub]
	
	hubs_to_remove = [k for k, v in node_occurrences.items() if v in top_hubs]
	
	related_tool_dataframe = related_tool_dataframe[~(related_tool_dataframe['source'].isin(list(hubs_to_remove)) | related_tool_dataframe['target'].isin(list(hubs_to_remove)))]
	
	# Remove edges between hubs that have 10 or more connections 
	node_occurrences = Counter(list(related_tool_dataframe['source'])+list(related_tool_dataframe['target']))

	hubs = [k for k, v in node_occurrences.items() if v >=max_edges]
	
	related_tool_dataframe = related_tool_dataframe[~(related_tool_dataframe['source'].isin(list(hubs)) & related_tool_dataframe['target'].isin(list(hubs)))]	

	# Write
	related_tool_dataframe.to_csv(outfile, sep='\t', index=False)

#############################################
########## 3. Get Nodes Tables
#############################################

# @transform(filterToolSimilarity,
# 		   suffix('edges.txt'),
# 		   add_inputs(prepareArticleTable),
# 		   'nodes.txt')
@transform(filterToolSimilarity,
		   suffix('edges.txt'),'nodes.txt')

def getNodeTables(infiles, outfile):

	edges_df = pd.read_table(infiles)

	all_dois = list(edges_df['source']) + list(edges_df['target'])

	dois_count = Counter(all_dois)

	df = pd.DataFrame(list(dois_count.items()), columns=['doi', 'node_count'])

	print(outfile + '\t' + "Average Number of Nodes: " + str(np.mean([v for k,v in dois_count.items()])) + '\n')

	df.to_csv(outfile, sep = '\t', index = False)

#############################################
########## 3. Gradually add edges
#############################################

def filterJobs2():
	# Create separate similarity networks - separate files with added edges
	for add_nodes in [x*200 for x in range(1,2)]:
		infile = 's6-tool_similarity.dir/related_tools.txt'
		outfile = 's7-graduallyaddededges.dir/related_tools_added{add_nodes}nodes.txt'.format(**locals())
		yield (infile, outfile, add_nodes)

@follows(getRelatedTools)
@follows(mkdir('s7-graduallyaddededges.dir'))
@files(filterJobs2)
def graduallyAddEdges(infile, outfile, add_nodes):

	# Print
	print('Doing {}...'.format(outfile))

	# Read related tool dataframe
	related_tool_dataframe = pd.read_table(infile).sort_values(['source', 'similarity'], ascending=False)

	# Remove duplicate edges 
	related_tool_dataframe = related_tool_dataframe.loc[~related_tool_dataframe[['source', 'target']].apply(sorted, axis=1).duplicated(keep='first')]
	
	# dataframe with 1 max edge per node 
	#one_edge = related_tool_dataframe.groupby(['source'], sort=False)['target']['similarity'].max())
	one_edge = related_tool_dataframe.groupby('source').apply(lambda x: x.loc[x.similarity == x.similarity.max(),['source','target','similarity']])
	print(one_edge.columns.values)
	one_edge.to_csv('trythis.csv',sep=',',index=True)
	# # nodes to add
	# extra_nodes = related_tool_dataframe[~(related_tool_dataframe['source'].isin(one_edge['source']) & related_tool_dataframe['target'].isin(one_edge['target']) & related_tool_dataframe['similarity'].isin(one_edge['similarity']))].reset_index(drop=True)
	# extra_nodes = extra_nodes.sort_values(by='similarity', ascending=False)
	
	# # add # of nodes
	# added_edges = one_edge.append(extra_nodes.iloc[0:add_nodes])

	# # Write
	# added_edges.to_csv(outfile, sep='\t', index=False)


#######################################################
#######################################################
########## S4. Dimensionality Reduction
#######################################################
#######################################################

#############################################
########## 1. Run T-SNE
#############################################
def filterJobs3():
	# Create separate tsne graphs for each  
	infile = ['s6-tool_similarity.dir/tool_similarity_dataframe.csv','s4-tables.dir/article-tool-table-merged.tsv']
	dims = [[1,2],[1,3],[2,3]]
	color_by = ['pub_year','journal_name']
	# outfile = ['s8-tsne.dir/tsne_dims{dim[0]}&{dim[1]}_colored_{category}.eps'.format(**locals()) for category in color_by for dim in dims]
	outfile = 's8-tsne.dir/tsne.csv'
	remove_na = ''
	outfile3D = os.getcwd()+'/'+'s8-tsne.dir/tSNE_3D_colored_'
	# outfile = []
	# for category in color_by:
	# 	for dim in dims:
	# 		outfile.append('s6-tsne.dir/tsne_dims{dim[0]}&{dim[1]}_colored_{category}.eps'.format(**locals()))
	yield (infile, outfile, dims, color_by, outfile3D, remove_na)

@follows(mkdir('s8-tsne.dir'))
@files(filterJobs3)

def runTsne(infile, outfile, dims, color_by, outfile3D, remove_na):

	r.run_tsne(infile, outfile, dims, color_by, outfile3D, remove_na)
	


#############################################
########## 1. Get Tool Topics - TSNE
############################################# 
@follows(mkdir('s10-tool_topics.dir'))
@merge((finalProcessing),
		['s10-tool_topics.dir/tsne_topics.csv','s10-tool_topics.dir/tsne_topics_threshold_5.csv'])

def getToolTopics(infiles, outfile):

	print('Processing abstracts.......')
	
	# Initialize dataframe
	abstract_dataframe = pd.read_table(infiles[0], sep = '\t')

	# Define stopwords
	# stopwords=nltk.corpus.stopwords.words("english")
	# stopwords.extend(['www','mail','edu','athttps', 'doi'])

	all_abstracts = []
	for i,x in enumerate(abstract_dataframe['abstract']):
		if int(abstract_dataframe['journal_fk'].iloc[i])==2 or int(abstract_dataframe['journal_fk'].iloc[i])==3: # database and nar abstracts were scraped without titles
			all_abstracts.append(str(json.loads(x)['abstract'][0]))
		else:
			abstract=' '.join([abstract_tuple[1] for abstract_tuple in json.loads(x)['abstract'] if abstract_tuple[0] and abstract_tuple[0].lower() not in [u'contact:', u'availability and implementation', u'supplementary information']])
			all_abstracts.append(abstract)
	abstract_dataframe['abstract']=all_abstracts
	
	def lemmatize_stemming(text):
		stemmer = PorterStemmer()
		return stemmer.stem(WordNetLemmatizer().lemmatize(text, pos='v'))
	def preprocess(text):
		result = []
		for token in gensim.utils.simple_preprocess(text):
			if token not in gensim.parsing.preprocessing.STOPWORDS and len(token) > 3:
				result.append(lemmatize_stemming(token)) # stemming
				#result.append(token)
		return result

	# remove urls and emails
	all_abstracts = [re.sub('\S*(\W?://\S+\s*)', '', ABS) for ABS in all_abstracts]
	all_abstracts = [re.sub('\S*(\W?@\S+\s*)', '', ABS) for ABS in all_abstracts]
	all_abstracts = [ABS.replace('(', '') for ABS in all_abstracts]
	all_abstracts = [ABS.replace(')', '') for ABS in all_abstracts]


	# Process abstracts
	processed_abstracts = [preprocess(ABS) for ABS in all_abstracts]

	# Get dictionary of all terms
	term_freq = gensim.corpora.Dictionary(processed_abstracts)
	print('Number of terms: ' + str(len(term_freq)))
	
	# density plot of term-doc frequencies
	num_docs = term_freq.num_docs
	print('Number documents: ' + str(num_docs))
	all_term_counts = [int(x) for x in list(term_freq.dfs.values())]
	sns.kdeplot(all_term_counts)
	#plt.hist(all_term_counts, bins='auto') 
	plt.xlim([min(all_term_counts),max(all_term_counts)])
	plt.savefig('s10-tool_topics.dir/term_frequencies.pdf',dpi = 500)
	plt.close()
	
	# Remove terms that occur in over % of abstracts and those that occur in fewer than 5 abstracts 
	thresh = 50
	term_freq.filter_extremes(no_below=0, no_above=thresh/100)
	print('Number of terms after filter of ' + str(thresh) + '% threshold: ' + str(len(term_freq)))

	# density plot of term frequencies
	all_term_counts = [int(x)for x in list(term_freq.dfs.values())]
	sns.kdeplot(all_term_counts)
	#plt.hist(all_term_counts, bins='auto') 
	plt.xlim([min(all_term_counts),max(all_term_counts)])
	plt.savefig('s10-tool_topics.dir/term_frequencies_threshold_' + str(thresh) + '.pdf',dpi = 500)
	plt.close()
	
	# Process abstracts 
	processed_abstracts_final =[]
	for pa in processed_abstracts:
		processed_abstracts_final.append([x for x in pa if x in list(term_freq.values())])

	processed_abstracts_final2 = []
	for pa in processed_abstracts_final:
		processed_abstracts_final2.append(str(' '.join(pa)))

	# Vectorize
	vectorizer = CountVectorizer()
	X = vectorizer.fit_transform(processed_abstracts_final2)

	# Find the best number of topics based on model perplexity 
	print('Finding best number of topics.........')	
	perplexity = []
	all_num_topics = [5,10,15,20,25,30,35,40,45,50,55]
	for num_topics in all_num_topics:
		print('Finding ' + str(num_topics) +' topics'+ '\n')
		lda_model = LatentDirichletAllocation(random_state=100,learning_method = 'online', max_iter=100,n_components=num_topics)
		lda_output = lda_model.fit_transform(X)
		print('Perplexity: ' + str(lda_model.perplexity(X)))
		print('***************')
		perplexity.append(lda_model.perplexity(X))
		
	# Plot perplexity vs # topics 
	plt.figure(figsize=(12, 8))
	plt.plot([5,10,15,20,25,30,35,40,45,50,55], perplexity)
	plt.xlabel("Topics", fontsize = 20)
	plt.ylabel("Perplexity",fontsize = 20)
	plt.xticks(np.arange(0, 55+1, 5),size = 12)
	plt.yticks(size = 12)
	plt.xlim([5,55])
	plt.savefig('s10-tool_topics.dir/perplexity_vs_topics.pdf',dpi = 1000, bbox_inches='tight')
	plt.close()  
	
	# Choose the best number of topics based on the lowest perplexity 
	idx_lowest_perplexity = perplexity.index(min(perplexity))   
	best_num_topics =   all_num_topics[idx_lowest_perplexity] 
	
	# Save perplexity results 
	df_perplexity = pd.DataFrame()
	df_perplexity['perplexity'] = perplexity
	df_perplexity['topics'] = all_num_topics
	df_perplexity.to_csv('s10-tool_topics.dir/perplexity_vs_topics.csv',sep=',', index=False)
	
	print('Best number of topics: ' + str(best_num_topics)+'\n') 
	print('Perplexity: ' +str(min(perplexity))+'\n')
	print('Creating final LDA model.........')
	
	# Run LDA with the best # topics 
	lda_model = LatentDirichletAllocation(random_state=100,learning_method = 'online', max_iter=100,n_components=best_num_topics)
	X_topics = lda_model.fit_transform(X) # matrix of each topic and abstract
	#X_topics = lda_outputs[idx_lowest_perplexity]


	# # Process abstracts
	# processed_abstracts = [P.process_text(x,'stem') for x in abstract_dataframe['abstract']]

	# # Vectorize
	# vectorizer = CountVectorizer()
	# X = vectorizer.fit_transform(processed_abstracts)
	
	# # find the best model parameters
	# search_params = {'n_components': [5, 10, 15, 20,30,50],'learning_decay':[0.5,0.7,0.9]}
	# lda = LatentDirichletAllocation(random_state=100,learning_method = 'online', max_iter=10)
	# model = GridSearchCV(lda, param_grid=search_params)
	# model.fit(X)
	# best_model = model.best_estimator_
	# print('*****************************************************************')
	# print("Best Model: ", model.best_params_)
	# print("Log Likelihood: ", model.best_score_)
	# print("Perplexity: ", best_model.perplexity(X))
	# print('*****************************************************************')
	
 	# # graph results
	#  # Get Log Likelyhoods from Grid Search Output
	# #likelihood = [round(score.mean_validation_score) for score in model.grid_scores_ ]
	# likelihood_ld5 = [round(score.mean_validation_score) for score in model.grid_scores_ if score.parameters['learning_decay']==0.5]
	# likelihood_ld7 = [round(score.mean_validation_score) for score in model.grid_scores_ if score.parameters['learning_decay']==0.7]
	# likelihood_ld9 = [round(score.mean_validation_score) for score in model.grid_scores_ if score.parameters['learning_decay']==0.9]

	# # Show graph
	# plt.figure(figsize=(12, 8))
	# plt.plot(search_params['n_components'], likelihood_ld5, label='0.5')
	# plt.plot(search_params['n_components'], likelihood_ld7 , label='0.7')
	# plt.plot(search_params['n_components'], likelihood_ld9, label='0.9')
	# #plt.plot(search_params['n_components'], likelihood)
	# plt.xlabel("Topics")
	# plt.ylabel("Log-Likelihood")
	# plt.legend(title='Learning decay', loc='best')
	# plt.savefig('lda_model_params.png')
	# plt.show()

	# # best parameters 
	# best_num_topics = model.best_params_['n_topics']
	# best_learning_decay = model.best_params_['learning_decay']
	
	# # LDA
	# #lda_model = LatentDirichletAllocation(n_topics=best_num_topics,learning_decay=best_learning_decay,random_state=100,max_iter=10)
	# lda_model = LatentDirichletAllocation(n_topics=10,random_state=100,max_iter=100,learning_decay=0.9)
	# X_topics = lda_model.fit_transform(X)
	# # print('******************************')
	# # print("Log Likelihood: ", lda_model.score(X))
	# # print("Perplexity: ", lda_model.perplexity(X))
	# # print(lda_model.get_params())
	
	def tsneWithThreshold(topics_matrix, threshold):

		# set a threshold to remove non-confident group assignments
		threshold_idx = np.amax(topics_matrix, axis=1) > threshold  # idx of doc that above the threshold
		#topics_matrix = topics_matrix[threshold_idx]
		
		# find most likely topic for each abstract
		lda_keys = []
		for i in range(topics_matrix.shape[0]):
			lda_keys.append(topics_matrix[i].argmax())

		# get the top 10 words for each topic 
		n_top_words = 10
		topic_descriptions = {}
		topic_word = lda_model.components_
		features = vectorizer.get_feature_names()  
		for i , topic in enumerate(topic_word):
			topic_words = np.array(features)[np.argsort(topic)][:-(n_top_words + 1):-1] 
			topic_descriptions[i]= str(' '.join(topic_words))

		# from sklearn.manifold import TSNE
		# tsne_model = TSNE(n_components=3)
		# tsne = tsne_model.fit_transform(X_topics)

		# run TSNE

		
		tsne = TSNE(n_components=3,perplexity=30.0)
		tsne_results = tsne.fit_transform(topics_matrix)

		
		tsne_results = pd.DataFrame(tsne_results )
		tsne_results.columns = ['V1', 'V2','V3']
		tsne_results['lda_key'] = lda_keys
		tsne_results['topic'] = [topic_descriptions[i] for i in lda_keys]
		tsne_results['doi'] = abstract_dataframe['doi']
		tsne_results['tool_name'] = abstract_dataframe['tool_name']
		tsne_results['pub_year'] = abstract_dataframe['pub_year']
		tsne_results['journal_name'] = abstract_dataframe['journal_name']
		tsne_results['tool_description'] = abstract_dataframe['tool_description']
		tsne_results['tool_homepage_url'] = abstract_dataframe['tool_homepage_url']
		tsne_results['total_pubmed_citations'] = abstract_dataframe['total_pubmed_citations']
		tsne_results['referenced_by_pub_years'] = abstract_dataframe['referenced_by_pub_years']
		tsne_results['up_down'] = abstract_dataframe['up_down']
		tsne_results_threshold = tsne_results[threshold_idx]
		return(tsne_results,tsne_results_threshold)

		# TSNE = pandas2ri.ri2py((r.run_tsne_topics(topics_matrix)))
		# TSNE = pd.DataFrame(TSNE)
		# TSNE.columns = ['V1', 'V2','V3']
		# TSNE['lda_key'] = lda_keys
		# TSNE['topic'] = [topic_descriptions[i] for i in lda_keys]
		# TSNE['doi'] = abstract_dataframe['doi']
		# TSNE['tool_name'] = abstract_dataframe['tool_name']
		# TSNE['pub_year'] = abstract_dataframe['pub_year']
		# TSNE['journal_name'] = abstract_dataframe['journal_name']
		# TSNE['tool_description'] = abstract_dataframe['tool_description']
		# TSNE['tool_homepage_url'] = abstract_dataframe['tool_homepage_url']
		# TSNE['total_pubmed_citations'] = abstract_dataframe['total_pubmed_citations']
		# TSNE['referenced_by_pub_years'] = abstract_dataframe['referenced_by_pub_years']
		# TSNE['up_down'] = abstract_dataframe['up_down']
		# TSNE_threshold = TSNE[threshold_idx]
		# return(TSNE,TSNE_threshold)

	#write to csv
	# tsne = tsneWithThreshold(X_topics,0)
	# tsne.to_csv(outfile[0], sep = ',', index = False)
	
	# #write to csv (with threshold)
	# tsne = tsneWithThreshold(X_topics,0.5)
	# tsne.to_csv(outfile[1], sep = ',', index = False)
	tsne,tsne_thresh = tsneWithThreshold(X_topics,0.5)
	tsne.to_csv(outfile[0], sep = ',', index = False)
	tsne_thresh.to_csv(outfile[1], sep = ',', index = False)
	

#############################################
########## 1. Citation T-SNE
#############################################
@follows(getPubmedCitations)
@follows(mkdir('s9-similarity_citation.dir'))
@merge((getPubmedCitations),
		's9-similarity_citation.dir/citation_similarity_matrix.csv')

def getCitationSimilarityMatrix(infiles,outfile):

	df = pd.DataFrame(pd.read_table(infiles[0], sep='\t'))

	# drop rows with no citation info
	df= df.dropna(subset=['total_pubmed_citations']).reset_index()

	# find constant to multiple citations by in order to normalize citation data by year published
	df_mean_citations_age = df.groupby(['pub_year'])['total_pubmed_citations'].mean().reset_index()
	max_mean_citation= max(df_mean_citations_age['total_pubmed_citations'])
	df_mean_citations_age['constants'] = [max_mean_citation/x for x in df_mean_citations_age['total_pubmed_citations']]

	# make a dict of year published --> constant 
	constant_dict = dict(zip(df_mean_citations_age['pub_year'], df_mean_citations_age['constants']))

	# normalize citations 
	df['citations_normalized']= [df['total_pubmed_citations'].iloc[ind]*constant_dict[x] for ind, x in enumerate(df['pub_year'])]

	# matrix of differences in citations 
	matrix = pd.DataFrame(np.absolute(np.subtract.outer(df['citations_normalized'],df['citations_normalized'])))

	# fill diagonal, name columns and rows
	np.fill_diagonal(matrix.values, np.nan)
	matrix.columns = df['doi']
	matrix.index = df['doi']
	
	# Save matrix to file
	matrix.to_csv(outfile, sep = ',',index=True)


def filterJobs4():
	# Create separate tsne graphs for each  
	infile = ['s9-similarity_citation.dir/citation_similarity_matrix.csv','s5-stats.dir/pmid_altmetrics_availability_affiliations_pubcitations.tsv']
	dims = [[1,2],[1,3],[2,3]]
	color_by = ['pub_year','journal_name']
	outfile = [os.getcwd()+'/'+'s9-similarity_citation.dir/tsne_dims{dim[0]}&{dim[1]}_colored_{category}.eps'.format(**locals()) for category in color_by for dim in dims]
	outfile3D = os.getcwd()+'/'+'s9-similarity_citation.dir/tSNE_3D_colored_'
	remove_na = 'total_pubmed_citations'
	# outfile = []
	# for category in color_by:
	# 	for dim in dims:
	# 		outfile.append('s6-tsne.dir/tsne_dims{dim[0]}&{dim[1]}_colored_{category}.eps'.format(**locals()))
	yield (infile, outfile, dims, color_by, outfile3D,remove_na)

@files(filterJobs4)
def runTsneCitations(infile, outfile, dims, color_by, outfile3D, remove_na):

	r.run_tsne(infile, outfile, dims, color_by, outfile3D, remove_na)
	

##################################################
##################################################
########## Run pipeline
##################################################
##################################################
pipeline_run([sys.argv[-1]], multiprocess=1, verbose=1)
print('Done!')


