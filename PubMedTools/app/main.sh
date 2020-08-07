#!/bin/bash
 
if [ -z "${PTH}" ]; then
   export PTH="$(dirname $0)/"
fi

echo "Starting bert and api"
bert-serving-start -model_dir=/app/biobert -num_worker=$1 -tuned_model_dir=/app/biobert/ -ckpt_name=model.ckpt-1000000 -cpu &
python3 /app/simtools.py

# echo "kill bert server"
# bert-serving-terminate -port 5555