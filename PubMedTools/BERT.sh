#!/bin/bash

# Classsify new tools with BERT (trained on BioBERT and fine-tuned on a classification tool/not task)
export BERT_BASE=./bert
echo "starting bert..."
python3 $BERT_BASE/run_classifier.py \
  --task_name=cola \
  --do_lower_case=False \
  --do_predict=true \
  --data_dir=$BERT_BASE/data \
  --vocab_file=$BERT_BASE/biobert/vocab.txt \
  --bert_config_file=$BERT_BASE/biobert/bert_config.json \
  --init_checkpoint=$BERT_BASE/bert_output/model.ckpt-212 \
  --max_seq_length=128 \
  --output_dir=$BERT_BASE/bert_output/