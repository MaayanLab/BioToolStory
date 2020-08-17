#!/bin/bash
cd /home/maayanlab/Tools/

# download Named Entity Recognition (NER) model
python3 -m spacy download en
python3 -m spacy download en_core_web_sm

# set start and end dates (YYYY/MM/dd)
start=$(date -d '-1 day' '+%Y/%m/%d')
end=$start

loop_index='0'

# download data and detect tools
python3 /app/1_collect_data.py $start $end $loop_index
echo "finished data collection"

python3 /app/2_Extract_tools.py $start $end
echo "finished extrecting tools"

# classify tools BERT
python3 /app/3_tool_analysis.py $start $end
echo "finished BERT"

# clean text, collect data from altmetric, collect number of citations from pubmed 
python3 /app/4_get_data.py $start $end
echo "finished metadata collection"

# create vector for each tool
#python3 /app/5_text2vec.py $start $end

# *** Immplement manual tool aproval ***

# push tools to biotoolstory
# python3 /app/6_pushtools.py $start $end
# echo "finished data upload to the website"

# Tweet new tools
#python3 /app/TwitterBot/posTools.py

# FAIRshake assessment of the tools
# python3 ...
