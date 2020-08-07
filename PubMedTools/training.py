# -*- coding: utf-8 -*-
"""Tools.ipynb

**Train BERT on classification of tool or not**

Download the pretrained model by BioBert
https://github.com/naver/biobert-pretrained
"""

# enable access to Google Drive file system
from google.colab import drive
drive.mount('/content/drive')

# clone bert
!git clone https://github.com/google-research/bert.git

# create directories for bert
!mkdir /content/drive/'My Drive'/BERTTOOLS/data
!mkdir /content/drive/'My Drive'/BERTTOOLS/bert_output

import pandas as pd
from sklearn.preprocessing import LabelEncoder
from sklearn.model_selection import train_test_split
from pandas import DataFrame
le = LabelEncoder()

"""--> Manually upload the CSV file "tools.csv" with texts labels (tools or not)"""

df = pd.read_csv("/content/drive/My Drive/BERTTOOLS/examples.csv")
df.loc[df['valid_tool'].str.contains('tool',na=False), 'valid_tool'] = 1
df.loc[df['valid_tool'].str.contains('database',na=False), 'valid_tool'] = 1
df.loc[df['valid_tool'].str.contains('-1',na=False), 'valid_tool'] = 0
df.loc[df['valid_tool'].str.contains('0',na=False), 'valid_tool'] = 0
df.loc[df['valid_tool'].str.contains('1',na=False), 'valid_tool'] = 1
df.loc[df['valid_tool'].str.contains('2',na=False), 'valid_tool'] = 1
df = df[df['valid_tool']!='UN']
df['Article.Abstract.AbstractText'] = df['Article.Abstract.AbstractText'].str.replace("[",'')
df['Article.Abstract.AbstractText'] = df['Article.Abstract.AbstractText'].str.replace("]",'')
df['Article.Abstract.AbstractText'] = df['Article.Abstract.AbstractText'].str.strip("'")
df['Article.Abstract.AbstractText'] = df['Article.Abstract.AbstractText'].str.strip('"')

set(df['valid_tool'].tolist())

df

# Creating train and test dataframes according to BERT
df_bert = pd.DataFrame({'index_col':df['PMID'],
            'label':le.fit_transform(df['valid_tool']),
            'alpha':['a']*df.shape[0],
            'text':df['Article.Abstract.AbstractText'].replace(r'\n',' ',regex=True)})

df_bert_train, df_bert_dev = train_test_split(df_bert, test_size=0.01)

# split into train and test
df_bert_train, df_test = train_test_split(df_bert, test_size=0.3)

# Creating test dataframe according to BERT
df_bert_test = pd.DataFrame({'index_col':df_test['index_col'],
                 'text':df_test['text'].replace(r'\n',' ',regex=True)})

# Saving dataframes to .tsv format as required by BERT
df_bert_train.to_csv('/content/drive/My Drive/BERTTOOLS/data/train.tsv', sep='\t', index=False, header=False)
df_bert_test.to_csv('/content/drive/My Drive/BERTTOOLS/data/test.tsv', sep='\t', index=False, header=True)
df.to_csv('/content/drive/My Drive/BERTTOOLS/data/full_data.csv', sep=',', index=False, header=True)
df_bert_dev.to_csv('/content/drive/My Drive/BERTTOOLS/data/dev.tsv', sep='\t', index=False, header=False)

!python3 ./bert/run_classifier.py \
    --task_name=cola \
    --do_train=true \
    --do_eval=true \
    --do_predict=true \
    --do_lower_case=False \
    --data_dir=/content/drive/'My Drive'/BERTTOOLS/data \
    --vocab_file=/content/drive/'My Drive'/BERTTOOLS/biobert/vocab.txt \
    --bert_config_file=/content/drive/'My Drive'/BERTTOOLS/biobert/bert_config.json \
    --init_checkpoint=/content/drive/'My Drive'/BERTTOOLS/biobert/model.ckpt-1000000 \
    --max_seq_length=128 \
    --train_batch_size=32 \
    --learning_rate=2e-5 \
    --num_train_epochs=3.0 \
    --output_dir=/content/drive/'My Drive'/BERTTOOLS/bert_output

df_results = pd.read_csv("/content/drive/My Drive/BERTTOOLS/bert_output/test_results.tsv",sep="\t",header=None)
df_results

df_results_csv = pd.DataFrame({'index_col':df_test['index_col'].tolist(),
                               'Is_Response':df_results.idxmax(axis=1)})
df_results_csv

x = pd.merge(df_test, df_results_csv, on='index_col')
x

"""**Precision Recall**"""

# https://stackabuse.com/text-classification-with-python-and-scikit-learn/
from sklearn.metrics import classification_report, confusion_matrix, accuracy_score
y_test = x['label'].tolist()
y_pred = x['Is_Response'].tolist()
print(confusion_matrix(y_test,y_pred))
print(classification_report(y_test,y_pred))
print(accuracy_score(y_test, y_pred))
