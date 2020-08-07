#!/bin/bash

# Classsify new tools with BERT (trained using BioBERT and fine-tuned on a classification tool/not task)

# instructions: change `init_checkpoint=$BERT_BASE` to be the path to your .ckpt file --> this is the weights of the trained model
export BERT_BASE=./bert
echo "starting bert..."
python3 $BERT_BASE/run_classifier.py \
  --task_name=cola \
  --do_lower_case=False \
  --do_predict=true \
  --data_dir=$BERT_BASE/data \
  --vocab_file=$BERT_BASE/biobert/vocab.txt \
  --bert_config_file=$BERT_BASE/biobert/bert_config.json \
  --init_checkpoint=$BERT_BASE/bert_output/model.ckpt-295 \
  --max_seq_length=128 \
  --output_dir=$BERT_BASE/bert_output/