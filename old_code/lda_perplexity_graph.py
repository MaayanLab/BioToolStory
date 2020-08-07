#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Mar 15 16:39:01 2019

@author: maayanlab
"""

import pandas as pd
import gensim
from gensim.utils import simple_preprocess
from gensim.parsing.preprocessing import STOPWORDS
from nltk.stem import WordNetLemmatizer, SnowballStemmer
from nltk.stem.porter import *
from nltk.stem import *
import numpy as np
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.decomposition import LatentDirichletAllocation
from sklearn.model_selection import GridSearchCV
np.random.seed(2018)
import nltk
nltk.download('wordnet')
import json
import re
stopwords=nltk.corpus.stopwords.words("english")
stopwords.extend(['www','mail','edu','athttps', 'doi'])

df = pd.DataFrame.from_csv('/Users/maayanlab/Desktop/11072018/bioinformatics-tool-paper-V2/s5-stats.dir/FINAL_bioinformatics_tools_analysis.csv',sep=',')


def lemmatize_stemming(text):
    stemmer = PorterStemmer()
    return stemmer.stem(WordNetLemmatizer().lemmatize(text, pos='v'))
def preprocess(text):
    result = []
    for token in gensim.utils.simple_preprocess(text):
        if token not in gensim.parsing.preprocessing.STOPWORDS and len(token) > 3:
            result.append(lemmatize_stemming(token))
    return result


all_abstracts = []
for i,x in enumerate(df['abstract']):
    if int(df['journal_fk'].iloc[i])==2 or int(df['journal_fk'].iloc[i])==3: # database and nar abstracts were scraped without titles
        all_abstracts.append(str(json.loads(x)['abstract'][0]))
    else:
        abstract=' '.join([abstract_tuple[1] for abstract_tuple in json.loads(x)['abstract'] if abstract_tuple[0] and abstract_tuple[0].lower() not in [u'contact:', u'availability and implementation', u'supplementary information']])
        all_abstracts.append(abstract)

# remove urls and emails
all_abstracts = [re.sub('\S*(\W?://\S+\s*)', '', ABS) for ABS in all_abstracts]
all_abstracts = [re.sub('\S*(\W?@\S+\s*)', '', ABS) for ABS in all_abstracts]
all_abstracts = [ABS.replace('(', '') for ABS in all_abstracts]
all_abstracts = [ABS.replace(')', '') for ABS in all_abstracts]


# Process abstracts
processed_abstracts = [preprocess(ABS) for ABS in all_abstracts]


term_freq = gensim.corpora.Dictionary(processed_abstracts)
term_freq.filter_extremes(no_below=5, no_above=0.75)


processed_abstracts_final =[]
for pa in processed_abstracts:
    processed_abstracts_final.append([x for x in pa if x in list(term_freq.values())])

processed_abstracts_final2 = []
for pa in processed_abstracts_final:
    processed_abstracts_final2.append(str(' '.join(pa)))

# Vectorize
vectorizer = CountVectorizer()
X = vectorizer.fit_transform(processed_abstracts_final2)
	

perplexity = []
for num_topics in [5,10,15,20,25,30,35,40,45,50,55]:
   lda_model = LatentDirichletAllocation(random_state=1000,learning_method = 'online', max_iter=100,n_components=num_topics)
   lda_output = lda_model.fit_transform(X)
   perplexity.append(lda_model.perplexity(X))
    
# Show graph
plt.figure(figsize=(12, 8))
plt.plot([5,10,15,20,25,30,35,40,45,50,55], perplexity)

#plt.plot(search_params['n_components'], likelihood)
plt.xlabel("Topics", fontsize = 20)
plt.ylabel("Perplexity",fontsize = 20)
plt.xticks(np.arange(0, 55+1, 5),size = 12)
plt.yticks(size = 12)
plt.show()    
 
    
   
   
   
   
   
   
   lda_model = gensim.models.LdaMulticore(bow_corpus, num_topics=num_topics, id2word=term_freq, passes=2, workers=4)




model = GridSearchCV(lda, param_grid=search_params)
model.fit(X)
best_model = model.best_estimator_
print('*****************************************************************')
print("Best Model: ", model.best_params_)
print("Log Likelihood: ", model.best_score_)
print("Perplexity: ", best_model.perplexity(X))
print('*****************************************************************')

likelihood_ld5 = [round(score.perplexity) for score in model.grid_scores_ ]
#########################################################################################################
processed_abstracts_final =[]
for pa in processed_abstracts:
    processed_abstracts_final.append([x for x in pa if x in list(term_freq.values())])

processed_abstracts_final2 = []
for pa in processed_abstracts_final:
    processed_abstracts_final2.append(str(' '.join(pa)))

# Vectorize
vectorizer = CountVectorizer()
X = vectorizer.fit_transform(processed_abstracts_final2)
	
# find the best model parameters
search_params = {'n_components': [5, 10]}   #'learning_decay':[0.5,0.7,0.9]
lda = LatentDirichletAllocation(random_state=1000,learning_method = 'online', max_iter=10)
model = GridSearchCV(lda, param_grid=search_params)
model.fit(X)
best_model = model.best_estimator_
print('*****************************************************************')
print("Best Model: ", model.best_params_)
print("Log Likelihood: ", model.best_score_)
print("Perplexity: ", best_model.perplexity(X))
print('*****************************************************************')

#########################################################################################################

# graph results
# Get Log Likelyhoods from Grid Search Output
#likelihood = [round(score.mean_validation_score) for score in model.grid_scores_ ]
likelihood_ld5 = [round(score.mean_validation_score) for score in model.grid_scores_ if score.parameters['learning_decay']==0.5]
likelihood_ld7 = [round(score.mean_validation_score) for score in model.grid_scores_ if score.parameters['learning_decay']==0.7]
likelihood_ld9 = [round(score.mean_validation_score) for score in model.grid_scores_ if score.parameters['learning_decay']==0.9]
    
# Show graph
plt.figure(figsize=(12, 8))
plt.plot(search_params['n_components'], likelihood_ld5, label='0.5')
plt.plot(search_params['n_components'], likelihood_ld7 , label='0.7')
plt.plot(search_params['n_components'], likelihood_ld9, label='0.9')
#plt.plot(search_params['n_components'], likelihood)
plt.xlabel("Topics")
plt.ylabel("Log-Likelihood")
plt.legend(title='Learning decay', loc='best')
plt.savefig('lda_model_params.png')
plt.show()
    







count = 0
for k, v in dictionary.iteritems():
    print(k, v)
    count += 1
    if count > 10:
        break
dictionary.filter_extremes(no_below=15, no_above=0.5, keep_n=100000)


bow_corpus = [dictionary.doc2bow(doc) for doc in processed_docs]

from gensim import corpora, models
tfidf = models.TfidfModel(bow_corpus)
corpus_tfidf = tfidf[bow_corpus]
from pprint import pprint
for doc in corpus_tfidf:
    pprint(doc)
    break

lda_model_tfidf = gensim.models.LdaMulticore(corpus_tfidf, num_topics=10, id2word=dictionary, passes=2, workers=4)
for idx, topic in lda_model_tfidf.print_topics(-1):
    print('Topic: {} Word: {}'.format(idx, topic))


    
    
