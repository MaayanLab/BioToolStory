#!/bin/bash
git clone bert https://github.com/google-research/bert.git
python3 training-setup.py
python3 python bert/run_classifier.py \
    --task_name=cola \
    --do_train=true \
    --do_eval=true \
    --do_predict=true \
    --do_lower_case=False \
    --data_dir=BERTTOOLS/data \
    --vocab_file=BERTTOOLS/biobert/vocab.txt \
    --bert_config_file=BERTTOOLS/biobert/bert_config.json \
    --init_checkpoint=BERTTOOLS/biobert/model.ckpt-1000000 \
    --max_seq_length=128 \
    --train_batch_size=32 \
    --learning_rate=2e-5 \
    --num_train_epochs=3.0 \
    --output_dir=BERTTOOLS/bert_output
python3 training-eval.py
