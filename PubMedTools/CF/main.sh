#!/bin/bash

# download model
python3 -m spacy download en_core_web_sm
sudo python3 -m spacy download en

# set dates to collect tools (articles) from Pubmed
export start='2000/01/01'
export end='2020/01/01'

python3 common_fund.py $start $end
python3 extract_tools.py $start $end
# classify tools BERT
python3 tool_analysis.py $start $end
# clean text, collect data from Altmetric, collect number of citations from pubmed
python3 get_data.py $start $end
# convert tools to vectors
python3 text2vec.py $start $end
#upload tools to the signature-common DB
python3 pushtools_cf.py
