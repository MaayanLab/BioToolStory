#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Feb  1 13:14:14 2019

@author: maayanlab
"""
import pandas as pd
import numpy as np
import bokeh.plotting as bp
from bokeh.plotting import save
from bokeh.models import HoverTool

df = pd.DataFrame.from_csv('tsne_topics.csv', sep = ',',header=0).reset_index()


X_topics = df['topic']
n_top_words = 10
colormap = np.array(['pink','blue','cornflowerblue','tan','limegreen','black','olive','plum','gold','blue','red','darkblue','green','darkorange','cyan','lightsalmon','greenyellow','darkgrey','magenta','peru'])
num_example = len(X_topics)

plot_lda = bp.figure(plot_width=1400, plot_height=1100,
                     tools="pan,wheel_zoom,box_zoom,reset,hover,previewsave",
                     x_axis_type=None, y_axis_type=None, min_border=1)
source = bp.ColumnDataSource({'x':df['V2'], 'y':df['V3'],"ToolName":df['tool_name'][:num_example],"Description": df['tool_description'][:num_example],'URL':df['tool_homepage_url'][:num_example],'Topic':df['topic'][:num_example], 'color' :colormap[df['lda_key']][:num_example]})
plot_lda.scatter(x='x', y='y', source= source,color='color',legend='Topic')
plot_lda.legend.label_text_font_size = '15pt'
plot_lda.legend.location = "top_right"               
# randomly choose a news (within a topic) coordinate as the crucial words coordinate

# hover tools
hover = plot_lda.select(dict(type=HoverTool))
hover.tooltips = {"Tool Name": "@ToolName" ,"Topic":"@Topic", "Description": "@Description","URL":"@URL"}
# save the plot
save(plot_lda, 'tsne_topics.html')

#################################################################################################################################

df = pd.DataFrame.from_csv('tsne_topics_threshold_5.csv', sep = ',',header=0).reset_index()


topic_conversion = {
        'databas gene genom annot abstract provid inform sequenc function includ': 'Genome Annotation Databases',
        'analysi user tool provid visual softwar allow gener interfac develop':'Other Analysis and Visualization Tools',
        'protein structur predict server interact bind function sequenc residu peptid':'Protein Structure Prediction Tools',
        'sequenc genom align read tool algorithm base gener high detect':'Genome Alignment Tools',
        'method model base gene approach algorithm perform analysi predict dataset':'Prediction Tools',
        'network gene interact pathway biolog ontolog function base model visual':'Interactive Biological Pathway Tools',
        'variant diseas associ genet phenotyp studi genom popul mutat variat':'Genetic Variant Association Tools',
        'mirna target transcript regul regulatori lncrna predict express rna microrna':'miRNA Target Tools',
        'drug target chemic compound metabol enzym molecul reaction screen activ': 'Drug and Compound Tools'
,
        
        }

df['topic'] = [topic_conversion[x] for x in df['topic']]

X_topics = df['topic']
n_top_words = 10
colormap = np.array(['pink','blue','cornflowerblue','tan','limegreen','black','olive','plum','gold','blue','red','darkblue','green','darkorange','cyan','lightsalmon','greenyellow','darkgrey','magenta','peru'])
num_example = len(X_topics)

plot_lda = bp.figure(plot_width=1400, plot_height=1100,
                     tools="pan,wheel_zoom,box_zoom,reset,hover,previewsave",
                     x_axis_type=None, y_axis_type=None, min_border=1)
source = bp.ColumnDataSource({'x':df['V2'], 'y':df['V3'],"ToolName":df['tool_name'][:num_example],"Description": df['tool_description'][:num_example],'URL':df['tool_homepage_url'][:num_example],'Topic':df['topic'][:num_example], 'color' :colormap[df['lda_key']][:num_example]})
plot_lda.scatter(x='x', y='y', source= source,color='color',legend='Topic')
plot_lda.legend.label_text_font_size = '18pt'
plot_lda.legend.location = "top_right"               
# randomly choose a news (within a topic) coordinate as the crucial words coordinate

# hover tools
hover = plot_lda.select(dict(type=HoverTool))
hover.tooltips = {"Tool Name": "@ToolName" ,"Topic":"@Topic", "Description": "@Description","URL":"@URL"}
# save the plot
save(plot_lda, 'tsne_topics_threshold_5.html')


#################################################################################################################################


df = pd.DataFrame.from_csv('tsne_topics_threshold_5.csv', sep = ',',header=0).reset_index()


topic_conversion = {
        'databas gene genom annot abstract provid inform sequenc function includ': 'Genome Annotation Databases',
        'analysi user tool provid visual softwar allow gener interfac develop':'Other Analysis and Visualization Tools',
        'protein structur predict server interact bind function sequenc residu peptid':'Protein Structure Prediction Tools',
        'sequenc genom align read tool algorithm base gener high detect':'Genome Alignment Tools',
        'method model base gene approach algorithm perform analysi predict dataset':'Prediction Tools',
        'network gene interact pathway biolog ontolog function base model visual':'Interactive Biological Pathway Tools',
        'variant diseas associ genet phenotyp studi genom popul mutat variat':'Genetic Variant Association Tools',
        'mirna target transcript regul regulatori lncrna predict express rna microrna':'miRNA Target Tools',
        'drug target chemic compound metabol enzym molecul reaction screen activ': 'Drug and Compound Tools'
,
        
        }

df['topic'] = [topic_conversion[x] for x in df['topic']]

X_topics = df['topic']
n_top_words = 10


from colour import Color
black = Color('red')
colors = list(black.range_to(Color("black"),11))


colormap_dict = {2008:colors[-1].hex,
                 2009:colors[-2].hex,
                 2010:colors[-3].hex,
                 2011:colors[-4].hex,
                 2012:colors[-5].hex,
                 2013:colors[-6].hex,
                 2014:colors[-7].hex,
                 2015:colors[-8].hex,
                 2016:colors[-9].hex,
                 2017:colors[-10].hex,
                 2018:colors[-11].hex
                 }

colormap = np.array([colormap_dict[x] for x in df['pub_year']])
num_example = len(X_topics)

plot_lda = bp.figure(plot_width=1400, plot_height=1100,
                     tools="pan,wheel_zoom,box_zoom,reset,hover,previewsave",
                     x_axis_type=None, y_axis_type=None, min_border=1)
source = bp.ColumnDataSource({'x':df['V2'], 'y':df['V3'],"ToolName":df['tool_name'][:num_example],"Year":df['pub_year'][:num_example],"Description": df['tool_description'][:num_example],'URL':df['tool_homepage_url'][:num_example],'Topic':df['topic'][:num_example], 'color' :colormap})
plot_lda.scatter(x='x', y='y', source= source,color='color',legend='Year')
plot_lda.legend.label_text_font_size = '18pt'
plot_lda.legend.location = "top_right"               
# randomly choose a news (within a topic) coordinate as the crucial words coordinate

# hover tools
hover = plot_lda.select(dict(type=HoverTool))
hover.tooltips = {"Tool Name": "@ToolName" ,"Topic":"@Topic", "Description": "@Description","URL":"@URL"}
# save the plot
save(plot_lda, 'tsne_topics_threshold_5_year.html')



#################################################################################################################################
df = pd.DataFrame.from_csv('tsne_topics_threshold_5.csv', sep = ',',header=0).reset_index()


topic_conversion = {
        'databas gene genom annot abstract provid inform sequenc function includ': 'Genome Annotation Databases',
        'analysi user tool provid visual softwar allow gener interfac develop':'Other Analysis and Visualization Tools',
        'protein structur predict server interact bind function sequenc residu peptid':'Protein Structure Prediction Tools',
        'sequenc genom align read tool algorithm base gener high detect':'Genome Alignment Tools',
        'method model base gene approach algorithm perform analysi predict dataset':'Prediction Tools',
        'network gene interact pathway biolog ontolog function base model visual':'Interactive Biological Pathway Tools',
        'variant diseas associ genet phenotyp studi genom popul mutat variat':'Genetic Variant Association Tools',
        'mirna target transcript regul regulatori lncrna predict express rna microrna':'miRNA Target Tools',
        'drug target chemic compound metabol enzym molecul reaction screen activ': 'Drug and Compound Tools'
,
        
        }

df['topic'] = [topic_conversion[x] for x in df['topic']]

X_topics = df['topic']
n_top_words = 10


total_citations = []
for ref_years in df['referenced_by_pub_years']:
    ref_years = str(ref_years.replace('[','').replace(']','')).replace("'",'')
    ref_years = ref_years.split(', ')
    ref_years = [int(x) for x in ref_years if x not in  ['','2011-2012']]
    ref_years = [x for x in ref_years if x >= 2017]
    total_citations.append(len(ref_years)) 

from colour import Color
black = Color('red')
colors = list(black.range_to(Color("black"),max(total_citations)+1))


colormap = np.array([colors[x].hex for x in total_citations])
num_example = len(X_topics)

plot_lda = bp.figure(plot_width=1400, plot_height=1100,
                     tools="pan,wheel_zoom,box_zoom,reset,hover,previewsave",
                     x_axis_type=None, y_axis_type=None, min_border=1)
source = bp.ColumnDataSource({'x':df['V2'], 'y':df['V3'],"ToolName":df['tool_name'][:num_example],"Total_Citations": [str(x) for x in total_citations],"Year":df['pub_year'][:num_example],"Description": df['tool_description'][:num_example],'URL':df['tool_homepage_url'][:num_example],'Topic':df['topic'][:num_example], 'color' :colormap})
plot_lda.scatter(x='x', y='y', source= source,color='color',)
plot_lda.legend.label_text_font_size = '18pt'
plot_lda.legend.location = "top_right"               
# randomly choose a news (within a topic) coordinate as the crucial words coordinate

# hover tools
hover = plot_lda.select(dict(type=HoverTool))
hover.tooltips = {"Tool Name": "@ToolName" ,"Topic":"@Topic", "Description": "@Description","URL":"@URL",'Total Citations':"@Total_Citations"}
# save the plot
save(plot_lda, 'tsne_topics_threshold_5_citations2017&2018.html')


#################################################################################################################################
df = pd.DataFrame.from_csv('tsne_topics_threshold_5.csv', sep = ',',header=0).reset_index()


topic_conversion = {
        'databas gene genom annot abstract provid inform sequenc function includ': 'Genome Annotation Databases',
        'analysi user tool provid visual softwar allow gener interfac develop':'Other Analysis and Visualization Tools',
        'protein structur predict server interact bind function sequenc residu peptid':'Protein Structure Prediction Tools',
        'sequenc genom align read tool algorithm base gener high detect':'Genome Alignment Tools',
        'method model base gene approach algorithm perform analysi predict dataset':'Prediction Tools',
        'network gene interact pathway biolog ontolog function base model visual':'Interactive Biological Pathway Tools',
        'variant diseas associ genet phenotyp studi genom popul mutat variat':'Genetic Variant Association Tools',
        'mirna target transcript regul regulatori lncrna predict express rna microrna':'miRNA Target Tools',
        'drug target chemic compound metabol enzym molecul reaction screen activ': 'Drug and Compound Tools'
,
        
        }

df['topic'] = [topic_conversion[x] for x in df['topic']]

X_topics = df['topic']
n_top_words = 10

colormap = []
total_citations = []
for ref_years in df['referenced_by_pub_years']:
    ref_years = str(ref_years.replace('[','').replace(']','')).replace("'",'')
    ref_years = ref_years.split(', ')
    ref_years = [int(x) for x in ref_years if x not in  ['','2011-2012']]
    ref_years = [x for x in ref_years if x == 2018]
    if len(ref_years)>0:
        total_citations.append('Cited 2018')
        colormap.append('red')
    else:
        total_citations.append('Not cited 2018')
        colormap.append('black')


num_example = len(X_topics)

plot_lda = bp.figure(plot_width=1400, plot_height=1100,
                     tools="pan,wheel_zoom,box_zoom,reset,hover,previewsave",
                     x_axis_type=None, y_axis_type=None, min_border=1)
source = bp.ColumnDataSource({'x':df['V2'], 'y':df['V3'],"ToolName":df['tool_name'][:num_example],"Cited":total_citations[:num_example],"Year":df['pub_year'][:num_example],"Description": df['tool_description'][:num_example],'URL':df['tool_homepage_url'][:num_example],'Topic':df['topic'][:num_example], 'color' :colormap[:num_example]})
plot_lda.scatter(x='x', y='y', source= source,color='color',legend='Cited')
plot_lda.legend.label_text_font_size = '18pt'
plot_lda.legend.location = "top_right"               
# randomly choose a news (within a topic) coordinate as the crucial words coordinate

# hover tools
hover = plot_lda.select(dict(type=HoverTool))
hover.tooltips = {"Tool Name": "@ToolName" ,"Topic":"@Topic", "Description": "@Description","URL":"@URL"}
# save the plot
save(plot_lda, 'tsne_topics_threshold_5_citations2017&2018.html')








    "#1f77b4", "#aec7e8", "#ff7f0e", "#ffbb78", "#2ca02c",
    "#d62728", "#ff9896", "#9467bd", "#c5b0d5",
    "#8c564b", "#c49c94", "#e377c2", "#f7b6d2", "#7f7f7f",
    "#c7c7c7", "#bcbd22", "#dbdb8d", "#17becf", "#9edae5",
     "#98df8a"