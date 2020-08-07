#!/bin/bash
cd /home/maayanlab/Tools/

# Every Sunday update of citations and Altmetric data
python3 7_dataupdate.py
echo "finished data update"